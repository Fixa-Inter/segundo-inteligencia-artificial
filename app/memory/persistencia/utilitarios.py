from app.core.clients.mongo import abrir_cliente_mongo
from app.core.config import MONGO_BANCO_DADOS, MONGO_COLLECTION_SESSOES
from datetime import datetime, timezone

sessoes_ativas: dict[tuple[int, str], str] = {}

def agora() -> datetime:
    return datetime.now(timezone.utc)

async def documento_id_da_sessao(session_id: str, user_id: int) -> str | None:
    chave = (user_id, session_id)
    doc_id = sessoes_ativas.get(chave)
    if doc_id:
        return doc_id

    async with abrir_cliente_mongo() as cliente:
        if not MONGO_BANCO_DADOS or not MONGO_COLLECTION_SESSOES:
            print("Informações de conexão com o MongoDB ausentes!")
        else:
            db = cliente[MONGO_BANCO_DADOS]
            collection_sessoes = db[MONGO_COLLECTION_SESSOES]
            doc = await collection_sessoes.find_one(
                {"user_id": user_id, "session_id": session_id, "resumo": {"$in": ["", None]}},
                {"_id": 1},
                sort=[("iniciada_em", -1)],
            )
            if not doc:
                return None

            sessoes_ativas[chave] = doc["_id"]
            return doc["_id"]
