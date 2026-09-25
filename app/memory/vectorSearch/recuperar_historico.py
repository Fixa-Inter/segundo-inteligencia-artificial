from qdrant_client import models
from app.memory.embedding.config import (
    gerar_embedding_documento
)
from app.core.config import (
    QDRANT_HISTORICO_COLLECTION
    ,MONGO_BANCO_DADOS
    ,MONGO_COLLECTION_SESSOES
)
from app.core.clients.qdrant import abrir_cliente_qdrant
from app.core.clients.mongo import abrir_cliente_mongo


async def recuperar_historico(
        user_id: int,
        busca: str = "",
        limite: int = 3
) -> list[dict]:
    if busca:
        vetor = await gerar_embedding_documento(busca)

        async with abrir_cliente_qdrant() as cliente:
            resultados = await cliente.query_points(
                collection_name=QDRANT_HISTORICO_COLLECTION,query=vetor,
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="user_id",
                            match=models.MatchValue(value=user_id),
                        )
                    ]
                ),
                limit=limite,
            )

            if resultados.points:
                return [
                    {
                        "doc_id":      ponto.id,
                        "iniciada_em": ponto.payload.get("iniciada_em", ""),
                        "resumo":      ponto.payload["resumo"],
                    }
                    for ponto in resultados.points
                ]

        async with abrir_cliente_mongo() as cliente:
            db = cliente[MONGO_BANCO_DADOS]
            collection_sessoes = db[MONGO_COLLECTION_SESSOES]
            filtro = {"user_id": user_id}
            docs = (
                collection_sessoes
                .find(filtro, {"resumo": 1, "iniciada_em": 1})
                .sort("iniciada_em", -1)
                .limit(limite)
            )

            return [
                {"doc_id": d["_id"], "iniciada_em": d["iniciada_em"], "resumo": d["resumo"]}
                async for d in docs
            ]

