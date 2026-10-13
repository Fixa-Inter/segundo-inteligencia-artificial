from langchain.tools import ToolRuntime, tool

from app.schemas.UsuarioContexto import UsuarioContexto
from app.services.solicitacoes.buscarSolicitacao import listar_solicitacoes_pendentes


@tool
async def listar_todas_solicitacoes_pendentes(runtime: ToolRuntime) -> dict:
    """Lista problemas pendentes no endereco do gestor autenticado.

Nao recebe argumentos da IA. O SELECT filtra status pendente e CNPJ do
endereco associado ao gestor."""
    contexto = runtime.context
    if not isinstance(contexto, dict) or not isinstance(contexto.get("usuario"), UsuarioContexto):
        raise ValueError("Forneça uma instância de UsuarioContexto em context['usuario'].")
    usuario = contexto["usuario"]
    if usuario.tipo_acesso.lower() != "gestor":
        return {
            "status": "ACESSO_NEGADO",
            "mensagem": "Somente gestores podem consultar as solicitações pendentes da organização.",
        }
    return await listar_solicitacoes_pendentes(usuario)
