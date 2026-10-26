from qdrant_client import models
from app.memory.embedding import (
    gerar_vetor_documento
)
from app.core.configuracao import (
    QDRANT_COLECAO_HISTORICO
    ,MONGO_BANCO_DADOS
    ,MONGO_COLECAO_SESSOES
)
from app.core.clients.qdrant import abrir_cliente_qdrant
from app.core.clients.mongo import abrir_cliente_mongo


async def recuperar_historico(
        usuario_id: int,
        busca: str = "",
        limite: int = 3
) -> list[dict]:
    if busca:
        vetor = await gerar_vetor_documento(busca)

        async with abrir_cliente_qdrant() as cliente:
            resultados = await cliente.query_points(
                collection_name=QDRANT_COLECAO_HISTORICO,query=vetor,
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="user_id",
                            match=models.MatchValue(value=usuario_id),
                        )
                    ]
                ),
                limit=limite,
            )

            if resultados.points:
                session_ids = [
                    ponto.payload.get("session_id")
                    for ponto in resultados.points
                    if ponto.payload.get("session_id")
                ]
                async with abrir_cliente_mongo() as cliente_mongo:
                    colecao = cliente_mongo[MONGO_BANCO_DADOS][MONGO_COLECAO_SESSOES]
                    cursor = colecao.find(
                        {
                            "user_id": usuario_id,
                            "session_id": {"$in": session_ids},
                            "esta_ativo": True,
                        },
                        {"session_id": 1},
                    )
                    sessoes_ativas = {
                        documento["session_id"]
                        for documento in await cursor.to_list(length=None)
                    }

                pontos_ativos = [
                    ponto for ponto in resultados.points
                    if ponto.payload.get("session_id") in sessoes_ativas
                ]
                if pontos_ativos:
                    return [
                        {
                            "doc_id": ponto.id,
                            "iniciada_em": ponto.payload.get("iniciada_em", ""),
                            "resumo": ponto.payload["resumo"],
                        }
                        for ponto in pontos_ativos
                    ]

    async with abrir_cliente_mongo() as cliente:
        banco = cliente[MONGO_BANCO_DADOS]
        colecao_sessoes = banco[MONGO_COLECAO_SESSOES]
        filtro = {"user_id": usuario_id, "esta_ativo": True}
        documentos = (
            colecao_sessoes
            .find(filtro, {"resumo": 1, "iniciada_em": 1, "mensagens": 1})
            .sort("iniciada_em", -1)
            .limit(limite)
        )

        historico = []
        async for d in documentos:
            # Conversas abertas podem ainda não ter resumo. Use os relatos humanos.
            resumo = d.get("resumo") or "\n".join(
                str(m.get("content", "")) for m in d.get("mensagens", [])
                if m.get("role") == "human"
            )
            if resumo:
                historico.append({"doc_id": d["_id"], "iniciada_em": d["iniciada_em"], "resumo": resumo})
        return historico
