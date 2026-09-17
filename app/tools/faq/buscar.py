from langchain.tools import tool
from app.memory.embedding.config import gerar_embedding_documento
from app.memory.vectorSearch.cliente import abrir_cliente_qdrant
from app.core.config import QDRANT_FAQ_COLLECTION


@tool
async def buscar_faq(question: str) -> str:
    """Busca no FAQ oficial os trechos mais relevantes para responder a pergunta."""
    vetor = gerar_embedding_documento(question)


    async with abrir_cliente_qdrant() as qdrant:
        resultados = await qdrant.query_points(
            collection_name=QDRANT_FAQ_COLLECTION,
            query=vetor,
            limit=6,
        )

        if not resultados.points:
            return "Nenhum trecho relevante encontrado no FAQ."

        return "\n\n".join(
            ponto.payload["page_content"] for ponto in resultados.points
        )