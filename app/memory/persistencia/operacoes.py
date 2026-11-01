"""Controle durável das gravações aprovadas no chat, sem dados de autenticação."""

from datetime import datetime, timezone

from app.core.clients.mongo import abrir_cliente_mongo
from app.core.configuracao import MONGO_BANCO_DADOS

COLECAO = "operacoes_chat"


async def preparar(documento: dict) -> dict:
    async with abrir_cliente_mongo() as cliente:
        colecao = cliente[MONGO_BANCO_DADOS][COLECAO]
        await colecao.update_one(
            {"_id": documento["_id"]}, {"$setOnInsert": documento}, upsert=True,
        )
        salvo = await colecao.find_one({"_id": documento["_id"]})
    if salvo is None or salvo["conteudo_hash"] != documento["conteudo_hash"]:
        raise ValueError("A operação mudou. Prepare e confira os dados novamente.")
    return salvo


async def obter(operacao_id: str, usuario_id: int, sessao_id: str) -> dict | None:
    async with abrir_cliente_mongo() as cliente:
        return await cliente[MONGO_BANCO_DADOS][COLECAO].find_one({
            "_id": operacao_id, "usuario_id": usuario_id, "sessao_id": sessao_id,
        })


async def iniciar(documento: dict, aprovacao: dict) -> bool:
    """Somente um executor pode retirar a operação do estado preparada."""
    async with abrir_cliente_mongo() as cliente:
        resultado = await cliente[MONGO_BANCO_DADOS][COLECAO].update_one(
            {"_id": documento["_id"], "usuario_id": documento["usuario_id"],
             "sessao_id": documento["sessao_id"], "conteudo_hash": documento["conteudo_hash"],
             "estado": "preparada"},
            {"$set": {"estado": "executando", "aprovacao": aprovacao,
                      "atualizada_em": datetime.now(timezone.utc)}},
        )
    return resultado.matched_count == 1


async def finalizar(documento: dict, resultado: dict) -> None:
    estado = "indeterminada" if resultado.get("status") == "RESULTADO_INDETERMINADO" else "concluida"
    async with abrir_cliente_mongo() as cliente:
        atualizado = await cliente[MONGO_BANCO_DADOS][COLECAO].update_one(
            {"_id": documento["_id"], "estado": "executando",
             "usuario_id": documento["usuario_id"], "sessao_id": documento["sessao_id"]},
            {"$set": {"estado": estado, "resultado": resultado,
                      "atualizada_em": datetime.now(timezone.utc)}},
        )
    if atualizado.matched_count != 1:
        raise RuntimeError("Não foi possível salvar o resultado da operação.")
