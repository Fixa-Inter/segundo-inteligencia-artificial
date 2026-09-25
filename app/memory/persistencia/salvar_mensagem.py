from fastapi import HTTPException, status
from app.memory.persistencia.sessoes.iniciar_sessao import iniciar_sessao
from app.memory.persistencia.utilitarios import documento_id_da_sessao, agora
from app.core.clients.mongo import abrir_cliente_mongo
from app.core.config import MONGO_BANCO_DADOS, MONGO_COLLECTION_SESSOES


async def salvar_mensagem(
    session_id: str,
    role: str,
    content: str,
    user_id: int
) -> None:

    doc_id = await documento_id_da_sessao(session_id, user_id)
    if not doc_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inicie uma conversa para salvar a mensagem!",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    async with abrir_cliente_mongo() as cliente:
        db = cliente[MONGO_BANCO_DADOS]
        collection_sessoes = db[MONGO_COLLECTION_SESSOES]
        await collection_sessoes.update_one(
            {"_id": doc_id, "user_id": user_id},
            {
                "$push": {"mensagens": {"role": role, "content": content}},
                "$set":  {"atualizada_em": agora()},
            },
        )
