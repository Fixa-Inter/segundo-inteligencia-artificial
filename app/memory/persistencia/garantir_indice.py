from app.core.clients.mongo import abrir_cliente_mongo
from app.core.configuracao import MONGO_BANCO_DADOS, MONGO_COLECAO_SESSOES

async def garantir_indice_persistencia():
    async with abrir_cliente_mongo() as cliente:
        banco = cliente[MONGO_BANCO_DADOS]
        colecao_sessoes = banco[MONGO_COLECAO_SESSOES]
        await colecao_sessoes.update_many(
            {"esta_ativo": {"$exists": False}},
            {"$set": {"esta_ativo": True}},
        )
        await colecao_sessoes.create_index([("user_id", 1), ("session_id", 1)])
        await colecao_sessoes.create_index("user_id")
        await colecao_sessoes.create_index("iniciada_em")
