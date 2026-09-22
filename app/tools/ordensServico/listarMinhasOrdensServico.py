from langchain.tools import ToolRuntime, tool

from app.schemas.UsuarioContexto import UsuarioContexto
from app.services.ordensServico.buscarOrdensServico import (
    consultar_minhas_ordens_servico,
)
from app.tools.ordensServico.utilitarios import montar_tabelas


@tool
async def listar_minhas_ordens_servico(runtime: ToolRuntime) -> dict:
    """Lista as OSs do técnico ou gestor autenticado, criadas nos últimos três meses.

    Não recebe argumentos da IA. Usa context['usuario'] e seu Bearer token.
    Retorna uma tabela Markdown por status, na ordem ATRASADA, PENDENTE,
    EM ANDAMENTO, CONCLUIDA; em cada grupo, prioridade ALTO, MÉDIO e BAIXO.
    Apresente integralmente o campo tabelas_markdown na resposta ao usuário,
    preservando as oito colunas e a ordenação. Data prevista nula aparece como
    Não informada. Informe também o período consultado; não invente OSs.
    """
    contexto = runtime.context

    if not isinstance(contexto, dict) or not isinstance(contexto.get("usuario"), UsuarioContexto):
        raise ValueError("Forneça uma instância de UsuarioContexto em context['usuario'].")
    
    usuario = contexto["usuario"]

    if usuario.tipo_acesso.lower() not in ("tecnico", "gestor"):
        return {
            "status": "ACESSO_NEGADO",
            "mensagem": "Somente técnicos e gestores podem consultar suas ordens de serviço.",
        }
    
    resultado = await consultar_minhas_ordens_servico(usuario.access_token)

    if resultado["status"] == "SUCESSO":
        resultado["tabelas_markdown"] = montar_tabelas(resultado["ordens_servico"])
        
    return resultado
