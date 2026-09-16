from langchain.tools import ToolRuntime, tool

from app.schemas.UsuarioContexto import UsuarioContexto
from app.services.solicitacoes.buscarSolicitacao import listar_solicitacoes_pendentes


@tool
async def buscar_todas_solicitacoes_pendentes(runtime: ToolRuntime) -> dict:
    """Lista as solicitações PENDENTES da organização do gestor autenticado.

    Não recebe argumentos da IA. Valida o tipo de acesso no contexto e usa
    o Bearer token para a API restringir a consulta ao endereço do usuário.
    Retorna título, data de criação, nome do usuário e status de cada solicitação.
    """
    contexto = runtime.context
    if not isinstance(contexto, dict) or not isinstance(contexto.get("usuario"), UsuarioContexto):
        raise ValueError("Forneça uma instância de UsuarioContexto em context['usuario'].")
    usuario = contexto["usuario"]
    if usuario.tipo_acesso.lower() != "gestor":
        return {
            "status": "ACESSO_NEGADO",
            "mensagem": "Somente gestores podem consultar as solicitações pendentes da organização.",
        }
    return await listar_solicitacoes_pendentes(usuario.access_token)
