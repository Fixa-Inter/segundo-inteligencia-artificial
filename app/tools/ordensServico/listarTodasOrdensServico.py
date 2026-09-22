from langchain.tools import ToolRuntime, tool

from app.schemas.UsuarioContexto import UsuarioContexto
from app.services.ordensServico.buscarOrdensServico import consultar_todas_ordens_servico
from app.tools.ordensServico.utilitarios import montar_tabelas


@tool
async def listar_todas_ordens_servico(runtime: ToolRuntime) -> dict:
    """Lista todas as OSs dos últimos três meses no escopo do gestor autenticado.

    Exclusiva para gestores. A API restringe os dados pelo Bearer token de
    context['usuario']; não recebe identificação nem filtros fornecidos pela IA.
    Apresente integralmente tabelas_markdown e informe o período consultado.
    As tabelas seguem ATRASADA, PENDENTE, EM ANDAMENTO e CONCLUIDA, com
    prioridades ALTO, MÉDIO e BAIXO em cada grupo. Não invente ordens.
    """
    contexto = runtime.context
    if not isinstance(contexto, dict) or not isinstance(contexto.get("usuario"), UsuarioContexto):
        raise ValueError("Forneça uma instância de UsuarioContexto em context['usuario'].")
    usuario = contexto["usuario"]
    if usuario.tipo_acesso.lower() != "gestor":
        return {
            "status": "ACESSO_NEGADO",
            "mensagem": "Somente gestores podem consultar todas as ordens de serviço.",
        }
    resultado = await consultar_todas_ordens_servico(usuario.access_token)
    if resultado["status"] == "SUCESSO":
        resultado["tabelas_markdown"] = montar_tabelas(resultado["ordens_servico"])
    return resultado
