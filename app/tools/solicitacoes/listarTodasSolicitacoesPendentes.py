from langchain.tools import ToolRuntime, tool

from app.schemas import UsuarioContexto
from app.services.solicitacoes import listar_solicitacoes_pendentes

from app.core.respostas import MENSAGENS


@tool
async def listar_todas_solicitacoes_pendentes(runtime: ToolRuntime) -> dict:
    """Lista ate cinco pendencias do gestor nos ultimos tres meses.

Nao recebe argumentos da IA. O SELECT filtra status pendente e CNPJ do
endereco associado ao gestor."""
    contexto = runtime.context
    if not isinstance(contexto, dict) or not isinstance(contexto.get("usuario"), UsuarioContexto):
        raise ValueError(MENSAGENS['forneca_uma_instancia_de_usuariocontexto_em_context_usuario'])
    usuario = contexto["usuario"]
    if usuario.tipo_acesso.lower() not in {"gestor", "administrador"}:
        return {
            "status": "ACESSO_NEGADO",
            "mensagem": MENSAGENS['somente_gestores_e_administradores_podem_consultar_as_solicitacoes_pendentes_da_organizacao'],
        }
    return await listar_solicitacoes_pendentes(usuario)
