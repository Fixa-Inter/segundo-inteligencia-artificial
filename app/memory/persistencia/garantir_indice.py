from app.core.clients.mongo import abrir_cliente_mongo
from app.core.config import MONGO_BANCO_DADOS, MONGO_COLLECTION_SESSOES

async def garantir_indice_persistencia():
    async with abrir_cliente_mongo() as cliente:
        db = cliente[MONGO_BANCO_DADOS]
        collection_sessoes = db[MONGO_COLLECTION_SESSOES]
        await collection_sessoes.create_index([("user_id", 1), ("session_id", 1)])
        await collection_sessoes.create_index("user_id")
        await collection_sessoes.create_index("iniciada_em")
