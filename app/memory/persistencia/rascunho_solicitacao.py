"""Persistência de rascunhos de solicitação e ocorrência e seus anexos por sessão."""

import uuid
from datetime import datetime, timezone
from typing import Any, Literal

from app.core.clients.mongo import abrir_cliente_mongo
from app.core.config import MONGO_BANCO_DADOS, MONGO_COLLECTION_SESSOES
from app.memory.persistencia.utilitarios import documento_id_da_sessao


TipoRascunho = Literal["solicitacao", "ocorrencia"]


def _campo_rascunho(tipo: TipoRascunho) -> str:
    if tipo not in {"solicitacao", "ocorrencia"}:
        raise ValueError("Tipo de rascunho inválido.")
    return f"{tipo}_pendente"


STATUS_ATIVOS = {
    "aguardando_confirmacao",
    "aguardando_imagem",
    "erro_api",
}


def _agora() -> datetime:
    return datetime.now(timezone.utc)


def _urls_validas(imagens: list[str]) -> list[str]:
    if not isinstance(imagens, list):
        return []
    return list(dict.fromkeys(
        imagem.strip()
        for imagem in imagens
        if isinstance(imagem, str) and imagem.strip()
    ))


async def adicionar_imagens_a_sessao(
    session_id: str,
    user_id: int,
    imagens: list[str],
) -> None:
    urls = _urls_validas(imagens)
    if not urls:
        return

    doc_id = await documento_id_da_sessao(session_id, user_id)
    if not doc_id:
        raise ValueError("Sessão não encontrada para salvar as imagens.")

    async with abrir_cliente_mongo() as cliente:
        collection = cliente[MONGO_BANCO_DADOS][MONGO_COLLECTION_SESSOES]
        documento = await collection.find_one(
            {"_id": doc_id, "user_id": user_id},
            {"solicitacao_pendente": 1, "ocorrencia_pendente": 1},
        )
        ativos = [
            (campo, documento.get(campo) or {})
            for campo in ("solicitacao_pendente", "ocorrencia_pendente")
            if documento and (documento.get(campo) or {}).get("status_fluxo") in STATUS_ATIVOS
        ]
        if ativos:
            campo, _ = max(ativos, key=lambda item: item[1].get(
                "atualizada_em", datetime.min,
            ).replace(tzinfo=timezone.utc))
            caminho = f"{campo}.imagens"
        else:
            caminho = "anexos_pendentes"

        await collection.update_one(
            {"_id": doc_id, "user_id": user_id},
            {
                "$addToSet": {caminho: {"$each": urls}},
                "$set": {"atualizada_em": _agora()},
            },
        )


async def salvar_rascunho_solicitacao(
    session_id: str,
    user_id: int,
    dados: dict[str, Any],
    *, tipo: TipoRascunho = "solicitacao",
) -> dict[str, Any]:
    campo = _campo_rascunho(tipo)
    doc_id = await documento_id_da_sessao(session_id, user_id)
    if not doc_id:
        raise ValueError("Sessão não encontrada para salvar o rascunho.")

    async with abrir_cliente_mongo() as cliente:
        collection = cliente[MONGO_BANCO_DADOS][MONGO_COLLECTION_SESSOES]
        documento = await collection.find_one(
            {"_id": doc_id, "user_id": user_id},
            {campo: 1, "anexos_pendentes": 1},
        )
        if not documento:
            raise ValueError("Sessão não encontrada para salvar o rascunho.")

        atual = documento.get(campo) or {}
        status_atual = atual.get("status_fluxo")
        if status_atual in {"enviando", "resultado_indeterminado"}:
            raise ValueError(
                "O envio anterior precisa ser reconciliado antes de abrir outro rascunho."
            )
        imagens = _urls_validas(
            atual.get("imagens", []) if status_atual in STATUS_ATIVOS else []
        )
        imagens.extend(
            url for url in _urls_validas(documento.get("anexos_pendentes", []))
            if url not in imagens
        )

        agora = _agora()
        rascunho = {
            "id": atual.get("id") if status_atual in STATUS_ATIVOS else str(uuid.uuid4()),
            "tipo": tipo,
            "status_fluxo": "aguardando_confirmacao",
            "confirmado": False,
            "dados": dados,
            "imagens": imagens,
            "problema_id_api": None,
            "status_backend": None,
            "criada_em": atual.get("criada_em", agora) if status_atual in STATUS_ATIVOS else agora,
            "atualizada_em": agora,
        }

        atualizacao: dict[str, Any] = {
            "$set": {
                campo: rascunho,
                "atualizada_em": agora,
            },
            "$unset": {"anexos_pendentes": ""},
        }
        if status_atual == "cadastrada":
            arquivo = "solicitacoes" if tipo == "solicitacao" else "ocorrencias"
            atualizacao["$push"] = {arquivo: atual}

        await collection.update_one(
            {"_id": doc_id, "user_id": user_id},
            atualizacao,
        )
        return rascunho


async def obter_rascunho_solicitacao(
    session_id: str,
    user_id: int,
    *, tipo: TipoRascunho = "solicitacao",
) -> dict[str, Any] | None:
    campo = _campo_rascunho(tipo)
    doc_id = await documento_id_da_sessao(session_id, user_id)
    if not doc_id:
        return None

    async with abrir_cliente_mongo() as cliente:
        collection = cliente[MONGO_BANCO_DADOS][MONGO_COLLECTION_SESSOES]
        documento = await collection.find_one(
            {"_id": doc_id, "user_id": user_id},
            {campo: 1},
        )
        if not documento:
            return None
        return documento.get(campo)


async def atualizar_rascunho_solicitacao(
    session_id: str,
    user_id: int,
    campos: dict[str, Any],
    *,
    status_esperados: set[str] | None = None,
    tipo: TipoRascunho = "solicitacao",
) -> bool:
    campo = _campo_rascunho(tipo)
    doc_id = await documento_id_da_sessao(session_id, user_id)
    if not doc_id:
        return False

    agora = _agora()
    atualizacoes = {
        f"{campo}.{chave}": valor
        for chave, valor in campos.items()
    }
    atualizacoes[f"{campo}.atualizada_em"] = agora
    atualizacoes["atualizada_em"] = agora

    filtro: dict[str, Any] = {"_id": doc_id, "user_id": user_id}
    if status_esperados is not None:
        filtro[f"{campo}.status_fluxo"] = {"$in": list(status_esperados)}

    async with abrir_cliente_mongo() as cliente:
        collection = cliente[MONGO_BANCO_DADOS][MONGO_COLLECTION_SESSOES]
        resultado = await collection.update_one(filtro, {"$set": atualizacoes})
        return resultado.modified_count == 1 or resultado.matched_count == 1
