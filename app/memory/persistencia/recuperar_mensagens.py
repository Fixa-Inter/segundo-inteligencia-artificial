from app.core.clients.mongo import abrir_cliente_mongo
from app.core.config import MONGO_BANCO_DADOS, MONGO_COLLECTION_SESSOES

async def recuperar_mensagens(doc_id: str, user_id: int) -> list[dict]:
    async with abrir_cliente_mongo() as cliente:
        db = cliente[MONGO_BANCO_DADOS]
        collection_sessoes = db[MONGO_COLLECTION_SESSOES]
        doc = await collection_sessoes.find_one({"_id": doc_id, "user_id": user_id}, {"mensagens": 1})
        return doc["mensagens"] if doc else []
