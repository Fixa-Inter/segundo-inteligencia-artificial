"""Rascunho de pesquisa de compras no documento MongoDB da sessão."""

from datetime import datetime, timezone
from uuid import uuid4

from app.core.clients.mongo import abrir_cliente_mongo
from app.core.configuracao import MONGO_BANCO_DADOS, MONGO_COLECAO_SESSOES
from app.memory.persistencia.utilitarios import obter_documento_sessao_id


CAMPO = "analise_compra_pendente"
STATUS_ATIVOS = {"coletando_dados", "aguardando_opcionais", "pronto_para_busca", "erro_busca"}


def _agora() -> datetime:
    return datetime.now(timezone.utc)


async def obter_analise_compra(sessao_id: str, usuario_id: int) -> dict | None:
    documento_id = await obter_documento_sessao_id(sessao_id, usuario_id)
    if not documento_id:
        return None
    async with abrir_cliente_mongo() as cliente:
        documento = await cliente[MONGO_BANCO_DADOS][MONGO_COLECAO_SESSOES].find_one(
            {"_id": documento_id, "user_id": usuario_id, "esta_ativo": True}, {CAMPO: 1},
        )
    return (documento or {}).get(CAMPO)


async def salvar_analise_compra(
    sessao_id: str, usuario_id: int, *, dados: dict,
    status_fluxo: str, opcionais_oferecidos: bool, turno_id: str,
    ultima_busca: dict | None = None, pergunta_pendente: str | None = None,
) -> dict:
    documento_id = await obter_documento_sessao_id(sessao_id, usuario_id)
    if not documento_id:
        raise ValueError("Sessão não encontrada para salvar a análise de compra.")
    agora = _agora()
    async with abrir_cliente_mongo() as cliente:
        colecao = cliente[MONGO_BANCO_DADOS][MONGO_COLECAO_SESSOES]
        documento = await colecao.find_one(
            {"_id": documento_id, "user_id": usuario_id, "esta_ativo": True}, {CAMPO: 1},
        )
        if not documento:
            raise ValueError("Sessão não encontrada para salvar a análise de compra.")
        atual = documento.get(CAMPO) or {}
        continuar = bool(atual) and not atual.get("pausado") and atual.get("status_fluxo") in STATUS_ATIVOS
        rascunho = {
            "id": atual.get("id") if continuar else str(uuid4()),
            "versao": atual.get("versao", 0) + 1 if continuar else 1,
            "turno_id": turno_id,
            "tipo": "analista_compras",
            "status_fluxo": status_fluxo,
            "pausado": False,
            "dados": dados,
            "opcionais_oferecidos": opcionais_oferecidos,
            "pergunta_pendente": pergunta_pendente,
            "ultima_busca": ultima_busca,
            "criada_em": atual.get("criada_em", agora) if continuar else agora,
            "atualizada_em": agora,
        }
        operacao = {"$set": {CAMPO: rascunho, "atualizada_em": agora}}
        if atual and not continuar:
            operacao["$push"] = {"analises_compra_arquivadas": atual}
        resultado = await colecao.update_one(
            {"_id": documento_id, "user_id": usuario_id, "esta_ativo": True, CAMPO: documento.get(CAMPO)},
            operacao,
        )
        if resultado.matched_count != 1:
            raise ValueError("A análise de compra mudou. Releia os dados antes de atualizar.")
    return rascunho


async def atualizar_analise_compra(
    sessao_id: str, usuario_id: int, *, id_analise: str,
    versao: int, status_esperado: str, campos: dict, exigir_ativo: bool = False,
) -> dict:
    documento_id = await obter_documento_sessao_id(sessao_id, usuario_id)
    if not documento_id:
        raise ValueError("Sessão de compras não encontrada.")
    agora = _agora()
    atualizacoes = {f"{CAMPO}.{chave}": valor for chave, valor in campos.items()}
    atualizacoes[f"{CAMPO}.atualizada_em"] = agora
    atualizacoes["atualizada_em"] = agora
    async with abrir_cliente_mongo() as cliente:
        colecao = cliente[MONGO_BANCO_DADOS][MONGO_COLECAO_SESSOES]
        filtro = {
            "_id": documento_id, "user_id": usuario_id, "esta_ativo": True,
            f"{CAMPO}.id": id_analise, f"{CAMPO}.versao": versao,
            f"{CAMPO}.status_fluxo": status_esperado,
        }
        if exigir_ativo:
            filtro[f"{CAMPO}.pausado"] = {"$ne": True}
        resultado = await colecao.update_one(filtro, {"$set": atualizacoes})
        if resultado.matched_count != 1:
            raise ValueError("A análise de compra mudou. Releia os dados antes de atualizar.")
    return await obter_analise_compra(sessao_id, usuario_id)
