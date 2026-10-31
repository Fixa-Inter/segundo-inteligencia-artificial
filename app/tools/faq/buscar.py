from langchain.tools import ToolRuntime, tool
from qdrant_client import models
from app.schemas import UsuarioContexto
from app.memory.embedding import gerar_vetor_documento
from app.core.clients.qdrant import abrir_cliente_qdrant
from app.core.configuracao import QDRANT_COLECAO_FAQ


@tool
async def buscar_faq(pergunta: str, runtime: ToolRuntime) -> str:
    """Busca trechos do FAQ exclusivo do perfil autenticado para responder à pergunta.

    Informe somente a pergunta. O perfil vem de context['usuario'], não da IA.
    """
    contexto = runtime.context

    if not isinstance(contexto, dict) or not isinstance(contexto.get("usuario"), UsuarioContexto):
        raise ValueError("Forneça uma instância de UsuarioContexto em context['usuario'].")
    
    perfil = contexto["usuario"].tipo_acesso.lower()

    if perfil not in {"solicitante", "tecnico", "gestor", "administrador"}:
        raise ValueError("Perfil de FAQ inválido.")
    # O administrador utiliza o mesmo conteúdo de FAQ do gestor.
    perfil_faq = "gestor" if perfil == "administrador" else perfil
    
    vetor = await gerar_vetor_documento(pergunta)

    async with abrir_cliente_qdrant() as qdrant:
        resultados = await qdrant.query_points(
            collection_name=QDRANT_COLECAO_FAQ,
            query=vetor,
            query_filter=models.Filter(must=[models.FieldCondition(
                key="perfil", match=models.MatchValue(value=perfil_faq),
            )]),
            with_payload=True,
            limit=6,
        )

        if not resultados.points:
            return "Nenhum trecho relevante encontrado no FAQ."

        return "\n\n".join(
            ponto.payload["page_content"] for ponto in resultados.points
        )
