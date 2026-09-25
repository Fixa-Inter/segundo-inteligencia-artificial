import uuid
from app.memory.persistencia.utilitarios import documento_id_da_sessao, agora, sessoes_ativas
from app.core.clients.mongo import abrir_cliente_mongo
from app.core.config import MONGO_BANCO_DADOS, MONGO_COLLECTION_SESSOES

async def iniciar_sessao(
        session_id: str,
        user_id: int
) -> None:
    if await documento_id_da_sessao(session_id, user_id):
        return

    doc_id = str(uuid.uuid4())
    agora_val  = agora()

    async with abrir_cliente_mongo() as cliente:
        db = cliente[MONGO_BANCO_DADOS]
        collection_sessoes = db[MONGO_COLLECTION_SESSOES]
        await collection_sessoes.insert_one({
            "_id":           doc_id,
            "session_id":    session_id,
            "user_id":       user_id,
            "iniciada_em":   agora_val,
            "atualizada_em": agora_val,
            "resumo":        "",
            "mensagens":     [],
        })
        sessoes_ativas[(user_id, session_id)] = doc_id
