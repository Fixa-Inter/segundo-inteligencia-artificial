from langchain.tools import ToolRuntime, tool

from app.schemas import UsuarioContexto
from app.services.ocorrencias import consultar_minhas_ocorrencias
from app.tools.ocorrencias.utilitarios import montar_tabela


@tool
async def listar_minhas_ocorrencias(runtime: ToolRuntime) -> dict:
    """Lista ate tres ocorrencias recentes do tecnico ou gestor nos ultimos tres meses.

Nao recebe argumentos da IA. O SELECT filtra usuario, CNPJ e periodo.
Apresente integralmente a tabela retornada."""
    contexto = runtime.context
    if not isinstance(contexto, dict) or not isinstance(contexto.get("usuario"), UsuarioContexto):
        raise ValueError("Forneça uma instância de UsuarioContexto em context['usuario'].")
    usuario = contexto["usuario"]
    if usuario.tipo_acesso.lower() not in ("tecnico", "gestor", "administrador"):
        return {
            "status": "ACESSO_NEGADO",
            "mensagem": "Somente técnicos e gestores podem consultar suas ocorrências.",
        }
    resultado = await consultar_minhas_ocorrencias(usuario)
    if resultado["status"] == "SUCESSO":
        resultado["tabela_markdown"] = montar_tabela(resultado["ocorrencias"])
    return resultado
