from langchain.tools import ToolRuntime, tool

from app.schemas import UsuarioContexto
from app.services.ordensServico import consultar_todas_ordens_servico
from app.tools.ordensServico.utilitarios import montar_tabelas


@tool
async def listar_todas_ordens_servico(runtime: ToolRuntime) -> dict:
    """Lista ate tres OS recentes do endereco do gestor nos ultimos tres meses.

Para gestores e administradores. O SELECT restringe os registros ao CNPJ do
endereco associado ao usuario autenticado. Apresente tabela e periodo."""
    contexto = runtime.context
    if not isinstance(contexto, dict) or not isinstance(contexto.get("usuario"), UsuarioContexto):
        raise ValueError("Forneça uma instância de UsuarioContexto em context['usuario'].")
    usuario = contexto["usuario"]
    if usuario.tipo_acesso.lower() not in {"gestor", "administrador"}:
        return {
            "status": "ACESSO_NEGADO",
            "mensagem": "Somente gestores e administradores podem consultar todas as ordens de serviço.",
        }
    resultado = await consultar_todas_ordens_servico(usuario)
    if resultado["status"] == "SUCESSO":
        resultado["tabelas_markdown"] = montar_tabelas(resultado["ordens_servico"])
    return resultado
