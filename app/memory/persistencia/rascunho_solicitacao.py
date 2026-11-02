"""Persistência de rascunhos de cadastro e seus anexos por sessão."""

import uuid
from datetime import datetime, timezone
from typing import Any, Literal

from app.core.clients.mongo import abrir_cliente_mongo
from app.core.configuracao import MONGO_BANCO_DADOS, MONGO_COLECAO_SESSOES
from app.memory.persistencia.utilitarios import obter_documento_sessao_id


TipoRascunho = Literal["solicitacao", "ocorrencia", "evento"]
ARQUIVOS_RASCUNHOS = {"solicitacao": "solicitacoes", "ocorrencia": "ocorrencias", "evento": "eventos"}


def _campo_rascunho(tipo: TipoRascunho) -> str:
    if tipo not in ARQUIVOS_RASCUNHOS:
        raise ValueError("Tipo de rascunho inválido.")
    return f"{tipo}_pendente"


STATUS_ATIVOS = {
    "coletando_dados",
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


def _anexos_legados(documento: dict, tipo: TipoRascunho) -> list[str]:
    if tipo == "evento":
        return []
    outros_ativos = any(
        (outro := documento.get(_campo_rascunho(outro_tipo)) or {}).get("status_fluxo") in STATUS_ATIVOS
        and not outro.get("pausado")
        for outro_tipo in ARQUIVOS_RASCUNHOS if outro_tipo != tipo
    )
    return [] if outros_ativos else _urls_validas(documento.get("anexos_pendentes", []))


async def obter_quantidade_anexos_pendentes(sessao_id: str, usuario_id: int) -> int:
    documento_id = await obter_documento_sessao_id(sessao_id, usuario_id)
    if not documento_id:
        return 0
    async with abrir_cliente_mongo() as cliente:
        colecao = cliente[MONGO_BANCO_DADOS][MONGO_COLECAO_SESSOES]
        documento = await colecao.find_one(
            {"_id": documento_id, "user_id": usuario_id, "esta_ativo": True},
            {"anexos_pendentes": 1},
        )
    return len(_urls_validas((documento or {}).get("anexos_pendentes", [])))


async def registrar_coleta_parcial(
    sessao_id: str, usuario_id: int, *, tipo: TipoRascunho,
    turno_id: str, relato: str,
) -> dict[str, Any]:
    """Guarda o relato do usuário sem exigir IDs ou propor um cadastro completo."""
    if not turno_id or not isinstance(relato, str):
        raise ValueError("O turno e o texto da coleta são obrigatórios.")
    campo = _campo_rascunho(tipo)
    documento_id = await obter_documento_sessao_id(sessao_id, usuario_id)
    if not documento_id:
        raise ValueError("Sessão não encontrada para salvar a coleta.")

    async with abrir_cliente_mongo() as cliente:
        colecao = cliente[MONGO_BANCO_DADOS][MONGO_COLECAO_SESSOES]
        documento = await colecao.find_one(
            {"_id": documento_id, "user_id": usuario_id, "esta_ativo": True},
            {**{_campo_rascunho(t): 1 for t in ARQUIVOS_RASCUNHOS}, "anexos_pendentes": 1},
        )
        if not documento:
            raise ValueError("Sessão não encontrada para salvar a coleta.")
        atual = documento.get(campo) or {}
        status = atual.get("status_fluxo")
        if status in {"enviando", "resultado_indeterminado"}:
            raise ValueError("O envio anterior precisa ser reconciliado antes de abrir outro rascunho.")
        relato_turno = {"turno_id": turno_id, "texto": relato.strip()} if relato.strip() else None
        if status in STATUS_ATIVOS and not atual.get("pausado"):
            if status != "coletando_dados" or relato_turno is None or any(
                item.get("turno_id") == turno_id for item in atual.get("relatos", [])
            ):
                return atual
            novo = {**atual, "relatos": [*atual.get("relatos", []), relato_turno],
                    "atualizada_em": _agora()}
            resultado = await colecao.update_one(
                {
                    "_id": documento_id,
                    "user_id": usuario_id,
                    "esta_ativo": True,
                    campo: documento.get(campo),
                },
                {"$set": {campo: novo, "atualizada_em": novo["atualizada_em"]}},
            )
            if resultado.matched_count != 1:
                raise ValueError("A coleta mudou. Releia os dados antes de atualizar.")
            return novo

        # Anexos legados sem tipo só podem ser migrados quando não há outra proposta ativa.
        anexos_legados = _anexos_legados(documento, tipo)
        agora = _agora()
        rascunho = {
            "id": str(uuid.uuid4()), "versao": 1, "turno_id": turno_id, "tipo": tipo,
            "status_fluxo": "coletando_dados", "confirmado": False,
            "dados_confirmados": {}, "pausado": False, "rotulos": {}, "dados": {},
            "relatos": [relato_turno] if relato_turno else [], "imagens": anexos_legados,
            "problema_id_api": None, "status_backend": None,
            "criada_em": agora, "atualizada_em": agora,
        }
        atualizacao: dict[str, Any] = {"$set": {campo: rascunho, "atualizada_em": agora}}
        if anexos_legados:
            atualizacao["$unset"] = {"anexos_pendentes": ""}
        if status == "cadastrada":
            arquivo = ARQUIVOS_RASCUNHOS[tipo]
            atualizacao["$push"] = {arquivo: atual}
        elif atual:
            atualizacao["$push"] = {"rascunhos_arquivados": atual}
        resultado = await colecao.update_one(
            {
                "_id": documento_id,
                "user_id": usuario_id,
                "esta_ativo": True,
                campo: documento.get(campo),
            },
            atualizacao,
        )
        if resultado.matched_count != 1:
            raise ValueError("A coleta mudou. Releia os dados antes de atualizar.")
        return rascunho


async def adicionar_imagens_sessao(
    sessao_id: str,
    usuario_id: int,
    imagens: list[str],
    *, tipo: TipoRascunho | None = None,
) -> None:
    if tipo == "evento":
        return
    urls = _urls_validas(imagens)
    if not urls:
        return

    documento_id = await obter_documento_sessao_id(sessao_id, usuario_id)
    if not documento_id:
        raise ValueError("Sessão não encontrada para salvar as imagens.")

    async with abrir_cliente_mongo() as cliente:
        colecao = cliente[MONGO_BANCO_DADOS][MONGO_COLECAO_SESSOES]
        documento = await colecao.find_one(
            {"_id": documento_id, "user_id": usuario_id, "esta_ativo": True},
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
            {"_id": documento_id, "user_id": usuario_id, "esta_ativo": True},
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
            {"_id": documento_id, "user_id": usuario_id, "esta_ativo": True},
            {**{_campo_rascunho(t): 1 for t in ARQUIVOS_RASCUNHOS}, "anexos_pendentes": 1},
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
            atual.get("imagens", []) if mesmo_rascunho and tipo != "evento" else []
        )
        anexos_legados = _anexos_legados(documento, tipo)
        imagens.extend(url for url in anexos_legados if url not in imagens)

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
            "relatos": atual.get("relatos", []) if mesmo_rascunho else [],
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
        }
        if anexos_legados:
            atualizacao["$unset"] = {"anexos_pendentes": ""}
        if status_atual == "cadastrada":
            arquivo = ARQUIVOS_RASCUNHOS[tipo]
            atualizacao["$push"] = {arquivo: atual}
        elif atual and not mesmo_rascunho:
            atualizacao["$push"] = {"rascunhos_arquivados": atual}

        resultado = await colecao.update_one(
            {
                "_id": documento_id,
                "user_id": usuario_id,
                "esta_ativo": True,
                campo: documento.get(campo),
            },
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
            {"_id": documento_id, "user_id": usuario_id, "esta_ativo": True},
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

    filtro: dict[str, Any] = {
        "_id": documento_id,
        "user_id": usuario_id,
        "esta_ativo": True,
    }
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
