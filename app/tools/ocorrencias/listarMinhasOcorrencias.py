from langchain.tools import ToolRuntime, tool

from app.schemas import UsuarioContexto
from app.services.ocorrencias import consultar_minhas_ocorrencias
from app.tools.ocorrencias.utilitarios import montar_tabela

from app.core.respostas import MENSAGENS


@tool
async def listar_minhas_ocorrencias(runtime: ToolRuntime) -> dict:
    """Lista ate tres ocorrencias recentes do tecnico ou gestor nos ultimos tres meses.

Nao recebe argumentos da IA. O SELECT filtra usuario, CNPJ e periodo.
Apresente integralmente a tabela retornada."""
    contexto = runtime.context
    if not isinstance(contexto, dict) or not isinstance(contexto.get("usuario"), UsuarioContexto):
        raise ValueError(MENSAGENS['forneca_uma_instancia_de_usuariocontexto_em_context_usuario'])
    usuario = contexto["usuario"]
    if usuario.tipo_acesso.lower() not in ("tecnico", "gestor", "administrador"):
        return {
            "status": "ACESSO_NEGADO",
            "mensagem": MENSAGENS['somente_tecnicos_e_gestores_podem_consultar_suas_ocorrencias'],
        }
    resultado = await consultar_minhas_ocorrencias(usuario)
    if resultado["status"] == "SUCESSO":
        resultado["tabela_markdown"] = montar_tabela(resultado["ocorrencias"])
    return resultado
