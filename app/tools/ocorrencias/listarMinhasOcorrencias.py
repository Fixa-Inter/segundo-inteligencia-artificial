from langchain.tools import ToolRuntime, tool

from app.schemas.UsuarioContexto import UsuarioContexto
from app.services.ocorrencias.buscarOcorrencias import consultar_minhas_ocorrencias
from app.tools.ocorrencias.utilitarios import montar_tabela


@tool
async def listar_minhas_ocorrencias(runtime: ToolRuntime) -> dict:
    """Lista as ocorrências do técnico ou gestor autenticado.

    Não recebe argumentos da IA. Usa o token de context['usuario']; a API
    aplica o período padrão de três meses. Apresente integralmente o campo
    tabela_markdown, preservando as oito colunas e a ordem dos registros.
    Datas são exibidas em DD-MM-AAAA; código de equipamento nulo aparece
    como Não informado. Não invente ocorrências em caso de erro ou lista vazia.
    """
    contexto = runtime.context
    if not isinstance(contexto, dict) or not isinstance(contexto.get("usuario"), UsuarioContexto):
        raise ValueError("Forneça uma instância de UsuarioContexto em context['usuario'].")
    usuario = contexto["usuario"]
    if usuario.tipo_acesso.lower() not in ("tecnico", "gestor"):
        return {
            "status": "ACESSO_NEGADO",
            "mensagem": "Somente técnicos e gestores podem consultar suas ocorrências.",
        }
    resultado = await consultar_minhas_ocorrencias(usuario.access_token)
    if resultado["status"] == "SUCESSO":
        resultado["tabela_markdown"] = montar_tabela(resultado["ocorrencias"])
    return resultado
