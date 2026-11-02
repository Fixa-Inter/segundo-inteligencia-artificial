from langchain.tools import ToolRuntime, tool

from app.schemas import UsuarioContexto
from app.services.ordensServico import consultar_todas_ordens_servico
from app.tools.ordensServico.utilitarios import montar_tabelas

from app.core.respostas import MENSAGENS


@tool
async def listar_todas_ordens_servico(runtime: ToolRuntime) -> dict:
    """Lista ate tres OS recentes do endereco do gestor nos ultimos tres meses.

Para gestores e administradores. O SELECT restringe os registros ao CNPJ do
endereco associado ao usuario autenticado. Apresente tabela e periodo."""
    contexto = runtime.context
    if not isinstance(contexto, dict) or not isinstance(contexto.get("usuario"), UsuarioContexto):
        raise ValueError(MENSAGENS['forneca_uma_instancia_de_usuariocontexto_em_context_usuario'])
    usuario = contexto["usuario"]
    if usuario.tipo_acesso.lower() not in {"gestor", "administrador"}:
        return {
            "status": "ACESSO_NEGADO",
            "mensagem": MENSAGENS['somente_gestores_e_administradores_podem_consultar_todas_as_ordens_de_servico'],
        }
    resultado = await consultar_todas_ordens_servico(usuario)
    if resultado["status"] == "SUCESSO":
        resultado["tabelas_markdown"] = montar_tabelas(resultado["ordens_servico"])
    return resultado
