from langchain.tools import ToolRuntime, tool

from app.schemas.UsuarioContexto import UsuarioContexto
from app.services.solicitacoes.buscarSolicitacao import listar_minhas_solicitacoes


@tool
async def listar_minhas_solicitacoes(runtime: ToolRuntime) -> dict:
    """Lista as solicitações criadas pelo usuário autenticado.

    Não recebe filtros nem identificação fornecida pela IA. Usa o token de
    context['usuario'] e retorna título, data de criação e nome do usuário.
    Uma lista vazia significa que não foram encontradas solicitações.
    """
    contexto = runtime.context
    if not isinstance(contexto, dict) or not isinstance(contexto.get("usuario"), UsuarioContexto):
        raise ValueError("Forneça uma instância de UsuarioContexto em context['usuario'].")

    return await listar_minhas_solicitacoes(contexto["usuario"].access_token)
