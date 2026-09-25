from qdrant_client import models
from app.memory.persistencia.utilitarios import documento_id_da_sessao, sessoes_ativas, agora
from app.memory.persistencia.gerar_resumo import gerar_resumo
from app.core.clients.mongo import abrir_cliente_mongo
from app.core.clients.qdrant import abrir_cliente_qdrant
from app.core.config import MONGO_BANCO_DADOS, MONGO_COLLECTION_SESSOES, QDRANT_HISTORICO_COLLECTION
from app.memory.embedding.config import gerar_embedding_documento


async def encerrar_sessao(session_id: str, user_id: int) -> str:
    chave = (user_id, session_id)
    doc_id = await documento_id_da_sessao(session_id, user_id)

    if not doc_id:
        return ""

    async with abrir_cliente_mongo() as cliente:
        db = cliente[MONGO_BANCO_DADOS]
        collection_sessoes = db[MONGO_COLLECTION_SESSOES]

        doc = await collection_sessoes.find_one({"_id": doc_id, "user_id": user_id})

        if not doc or not doc.get("mensagens"):
            sessoes_ativas.pop(chave, None)
            return ""

        resumo = await gerar_resumo(doc["mensagens"])

        await collection_sessoes.update_one(
            {"_id": doc_id, "user_id": user_id},
            {"$set": {"resumo": resumo, "atualizada_em": agora()}},
        )

        sessoes_ativas.pop(chave, None)
        vetor = await gerar_embedding_documento(resumo)
        async with abrir_cliente_qdrant() as cliente_qdrant:
            await cliente_qdrant.upsert(
                collection_name=QDRANT_HISTORICO_COLLECTION,points=[
                    models.PointStruct(
                        id=doc_id,
                        vector=vetor,
                        payload={
                            "user_id":     user_id,
                            "session_id":  session_id,
                            "resumo":      resumo,
                            "iniciada_em": doc["iniciada_em"].isoformat(),
                        },
                    )
                ],
            )

    return resumo
