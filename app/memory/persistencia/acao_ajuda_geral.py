"""Proposta de edição do ajuda_geral vinculada ao usuário e à sessão."""

from datetime import datetime, timezone
from uuid import uuid4

from app.core.clients.mongo import abrir_cliente_mongo
from app.core.configuracao import MONGO_BANCO_DADOS, MONGO_COLECAO_SESSOES
from app.memory.persistencia.utilitarios import obter_documento_sessao_id


def _agora():
    return datetime.now(timezone.utc)


async def obter_acao(sessao_id: str, usuario_id: int) -> dict | None:
    documento_id = await obter_documento_sessao_id(sessao_id, usuario_id)
    if documento_id is None:
        return None
    async with abrir_cliente_mongo() as cliente:
        colecao = cliente[MONGO_BANCO_DADOS][MONGO_COLECAO_SESSOES]
        documento = await colecao.find_one(
            {"_id": documento_id, "user_id": usuario_id, "esta_ativo": True},
            {"ajuda_geral_pendente": 1},
        )
    return (documento or {}).get("ajuda_geral_pendente")


async def salvar_acao(sessao_id: str, usuario_id: int, dados: dict) -> dict:
    documento_id = await obter_documento_sessao_id(sessao_id, usuario_id)
    if documento_id is None:
        raise ValueError("Sessão não encontrada para confirmar a edição.")
    acao = {
        **dados,
        "id": str(uuid4()),
        "criada_em": _agora(),
    }
    async with abrir_cliente_mongo() as cliente:
        colecao = cliente[MONGO_BANCO_DADOS][MONGO_COLECAO_SESSOES]
        resultado = await colecao.update_one(
            {
                "_id": documento_id, "user_id": usuario_id, "esta_ativo": True,
                "ajuda_geral_pendente.status": {"$nin": ["executando", "resultado_indeterminado"]},
            },
            {"$set": {"ajuda_geral_pendente": acao, "atualizada_em": _agora()}},
        )
    if resultado.matched_count != 1:
        raise ValueError("Sessão não encontrada para confirmar a edição.")
    return acao


async def atualizar_acao(
    sessao_id: str, usuario_id: int, acao_id: str, campos: dict,
    *, status: str,
) -> bool:
    documento_id = await obter_documento_sessao_id(sessao_id, usuario_id)
    if documento_id is None:
        return False
    async with abrir_cliente_mongo() as cliente:
        colecao = cliente[MONGO_BANCO_DADOS][MONGO_COLECAO_SESSOES]
        resultado = await colecao.update_one(
            {
                "_id": documento_id, "user_id": usuario_id, "esta_ativo": True,
                "ajuda_geral_pendente.id": acao_id,
                "ajuda_geral_pendente.status": status,
            },
            {"$set": {
                **{f"ajuda_geral_pendente.{chave}": valor for chave, valor in campos.items()},
                "atualizada_em": _agora(),
            }},
        )
    return resultado.matched_count == 1


async def iniciar_acao(sessao_id: str, usuario_id: int, acao_id: str) -> bool:
    return await atualizar_acao(
        sessao_id, usuario_id, acao_id, {"status": "executando"},
        status="aguardando_confirmacao",
    )
