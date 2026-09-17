from langchain.tools import ToolRuntime, tool
from qdrant_client import models
from app.schemas.UsuarioContexto import UsuarioContexto
from app.memory.embedding.config import gerar_embedding_documento
from app.memory.vectorSearch.cliente import abrir_cliente_qdrant
from app.core.config import QDRANT_FAQ_COLLECTION


@tool
async def buscar_faq(question: str, runtime: ToolRuntime) -> str:
    """Busca trechos do FAQ exclusivo do perfil autenticado para responder à pergunta.

    Informe somente a pergunta. O perfil vem de context['usuario'], não da IA.
    """
    contexto = runtime.context

    if not isinstance(contexto, dict) or not isinstance(contexto.get("usuario"), UsuarioContexto):
        raise ValueError("Forneça uma instância de UsuarioContexto em context['usuario'].")
    
    perfil = contexto["usuario"].tipo_acesso.lower()

    if perfil not in {"solicitante", "tecnico", "gestor"}:
        raise ValueError("Perfil de FAQ inválido.")
    
    vetor = await gerar_embedding_documento(question)

    async with abrir_cliente_qdrant() as qdrant:
        resultados = await qdrant.query_points(
            collection_name=QDRANT_FAQ_COLLECTION,
            query=vetor,
            query_filter=models.Filter(must=[models.FieldCondition(
                key="perfil", match=models.MatchValue(value=perfil),
            )]),
            with_payload=True,
            limit=6,
        )

        if not resultados.points:
            return "Nenhum trecho relevante encontrado no FAQ."

        return "\n\n".join(
            ponto.payload["page_content"] for ponto in resultados.points
        )
