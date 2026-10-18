"""Persistência de rascunhos de solicitação e ocorrência e seus anexos por sessão."""

import uuid
from datetime import datetime, timezone
from typing import Any, Literal

from app.core.clients.mongo import abrir_cliente_mongo
from app.core.configuracao import MONGO_BANCO_DADOS, MONGO_COLECAO_SESSOES
from app.memory.persistencia.utilitarios import obter_documento_sessao_id


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


async def adicionar_imagens_sessao(
    sessao_id: str,
    usuario_id: int,
    imagens: list[str],
    *, tipo: TipoRascunho | None = None,
) -> None:
    urls = _urls_validas(imagens)
    if not urls:
        return

    documento_id = await obter_documento_sessao_id(sessao_id, usuario_id)
    if not documento_id:
        raise ValueError("Sessão não encontrada para salvar as imagens.")

    async with abrir_cliente_mongo() as cliente:
        colecao = cliente[MONGO_BANCO_DADOS][MONGO_COLECAO_SESSOES]
        documento = await colecao.find_one(
            {"_id": documento_id, "user_id": usuario_id},
            {"solicitacao_pendente": 1, "ocorrencia_pendente": 1},
        )
        ativos = [
            (campo, documento.get(campo) or {})
            for campo in ("solicitacao_pendente", "ocorrencia_pendente")
            if documento and (documento.get(campo) or {}).get("status_fluxo") in STATUS_ATIVOS
            and not (documento.get(campo) or {}).get("pausado")
            and (tipo is None or campo == _campo_rascunho(tipo))
        ]
        if ativos:
            campo, _ = max(ativos, key=lambda item: item[1].get(
                "atualizada_em", datetime.min,
            ).replace(tzinfo=timezone.utc))
            caminho = f"{campo}.imagens"
        else:
            caminho = "anexos_pendentes"

        await colecao.update_one(
            {"_id": documento_id, "user_id": usuario_id},
            {
                "$addToSet": {caminho: {"$each": urls}},
                "$set": {"atualizada_em": _agora()},
            },
        )


async def salvar_rascunho_solicitacao(
    sessao_id: str,
    usuario_id: int,
    dados: dict[str, Any],
    *, tipo: TipoRascunho = "solicitacao", turno_id: str,
    rotulos: dict[str, str] | None = None,
) -> dict[str, Any]:
    if not turno_id:
        raise ValueError("Informe o turno que produziu a proposta.")
    campo = _campo_rascunho(tipo)
    documento_id = await obter_documento_sessao_id(sessao_id, usuario_id)
    if not documento_id:
        raise ValueError("Sessão não encontrada para salvar o rascunho.")

    async with abrir_cliente_mongo() as cliente:
        colecao = cliente[MONGO_BANCO_DADOS][MONGO_COLECAO_SESSOES]
        documento = await colecao.find_one(
            {"_id": documento_id, "user_id": usuario_id},
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
        mesmo_rascunho = status_atual in STATUS_ATIVOS and not atual.get("pausado")
        if mesmo_rascunho and atual.get("dados") == dados and atual.get("turno_id"):
            return atual
        confirmados = {
            chave: valor for chave, valor in atual.get("dados_confirmados", {}).items()
            if mesmo_rascunho and chave in dados and dados[chave] == valor
        }
        imagens = _urls_validas(
            atual.get("imagens", []) if mesmo_rascunho else []
        )
        imagens.extend(
            url for url in _urls_validas(documento.get("anexos_pendentes", []))
            if url not in imagens
        )

        agora = _agora()
        rascunho = {
            "id": atual.get("id") if mesmo_rascunho else str(uuid.uuid4()),
            "versao": atual.get("versao", 0) + 1 if mesmo_rascunho else 1,
            "turno_id": turno_id,
            "tipo": tipo,
            "status_fluxo": "aguardando_confirmacao",
            "confirmado": False,
            "dados_confirmados": confirmados,
            "pausado": False,
            "rotulos": rotulos or {},
            "dados": dados,
            "imagens": imagens,
            "problema_id_api": None,
            "status_backend": None,
            "criada_em": atual.get("criada_em", agora) if mesmo_rascunho else agora,
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
        elif atual and not mesmo_rascunho:
            atualizacao["$push"] = {"rascunhos_arquivados": atual}

        resultado = await colecao.update_one(
            {"_id": documento_id, "user_id": usuario_id, campo: documento.get(campo)},
            atualizacao,
        )
        if resultado.matched_count != 1:
            raise ValueError("A proposta mudou. Releia os dados antes de atualizar.")
        return rascunho


async def obter_rascunho_solicitacao(
    sessao_id: str,
    usuario_id: int,
    *, tipo: TipoRascunho = "solicitacao",
) -> dict[str, Any] | None:
    campo = _campo_rascunho(tipo)
    documento_id = await obter_documento_sessao_id(sessao_id, usuario_id)
    if not documento_id:
        return None

    async with abrir_cliente_mongo() as cliente:
        colecao = cliente[MONGO_BANCO_DADOS][MONGO_COLECAO_SESSOES]
        documento = await colecao.find_one(
            {"_id": documento_id, "user_id": usuario_id},
            {campo: 1},
        )
        if not documento:
            return None
        return documento.get(campo)


async def atualizar_rascunho_solicitacao(
    sessao_id: str,
    usuario_id: int,
    campos: dict[str, Any],
    *,
    status_esperados: set[str] | None = None,
    tipo: TipoRascunho = "solicitacao",
    rascunho_id: str | None = None,
    versao: int | None = None,
    exigir_ativo: bool = False,
) -> bool:
    campo = _campo_rascunho(tipo)
    documento_id = await obter_documento_sessao_id(sessao_id, usuario_id)
    if not documento_id:
        return False

    agora = _agora()
    atualizacoes = {
        f"{campo}.{chave}": valor
        for chave, valor in campos.items()
    }
    atualizacoes[f"{campo}.atualizada_em"] = agora
    atualizacoes["atualizada_em"] = agora

    filtro: dict[str, Any] = {"_id": documento_id, "user_id": usuario_id}
    if exigir_ativo:
        filtro[f"{campo}.pausado"] = {"$ne": True}
    if rascunho_id is not None:
        filtro[f"{campo}.id"] = rascunho_id
    if versao is not None:
        if versao == 1:
            filtro["$or"] = [{f"{campo}.versao": 1}, {f"{campo}.versao": {"$exists": False}}]
        else:
            filtro[f"{campo}.versao"] = versao
    if status_esperados is not None:
        filtro[f"{campo}.status_fluxo"] = {"$in": list(status_esperados)}

    async with abrir_cliente_mongo() as cliente:
        colecao = cliente[MONGO_BANCO_DADOS][MONGO_COLECAO_SESSOES]
        resultado = await colecao.update_one(filtro, {"$set": atualizacoes})
        return resultado.modified_count == 1 or resultado.matched_count == 1
