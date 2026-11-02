from langchain.agents import create_agent
from langchain.agents.middleware import ToolCallLimitMiddleware
from langchain_core.messages import ToolMessage
from app.graph import ContextoGrafo
from app.tools.memoria import buscar_historico
from app.tools.visualizacoes import FERRAMENTAS_VISUALIZACOES
from app.schemas.visualizacao import ResultadoConsultaVisualizacao
from app.services.visualizacoes.limites import MAXIMO_CONSULTAS_POR_EXECUCAO

from app.agents.agentsResult import VisualizacaoResultado

from app.core.respostas import MENSAGENS


class LimiteConsultasVisualizacao(ToolCallLimitMiddleware):
    """Orçamento compartilhado das seis tools, contado antes do lote executar.

    A seleção do grupo estende o filtro da versão instalada do middleware.
    Histórico e a ferramenta de resposta estruturada não consomem esse limite.
    """

    def __init__(self):
        super().__init__(run_limit=MAXIMO_CONSULTAS_POR_EXECUCAO, exit_behavior="continue")
        self.ferramentas_analiticas = frozenset(t.name for t in FERRAMENTAS_VISUALIZACOES)

    def _matches_tool_filter(self, tool_call):
        return tool_call["name"] in self.ferramentas_analiticas

    def after_model(self, state, runtime):
        atualizacao = super().after_model(state, runtime)
        if atualizacao and atualizacao.get("messages"):
            conteudo = ResultadoConsultaVisualizacao(
                status="ERRO_VALIDACAO",
                mensagem=(
                    MENSAGENS['limite_de_consultas_desta_execucao_atingido_finalize_com_os_resultados_ja_obtidos']
                ),
            ).model_dump_json()
            atualizacao["messages"] = [
                ToolMessage(content=conteudo, tool_call_id=m.tool_call_id, name=m.name, status="error")
                if isinstance(m, ToolMessage) and m.name in self.ferramentas_analiticas else m
                for m in atualizacao["messages"]
            ]
        return atualizacao


def criar_agente_visualizacao(modelo, instrucao: str, ferramentas=None):
    ferramentas_por_nome = {}
    for ferramenta in [*FERRAMENTAS_VISUALIZACOES, buscar_historico, *(ferramentas or [])]:
        ferramentas_por_nome.setdefault(ferramenta.name, ferramenta)
    return create_agent(
        model=modelo,
        system_prompt=instrucao,
        tools=list(ferramentas_por_nome.values()),
        middleware=[LimiteConsultasVisualizacao()],
        context_schema=ContextoGrafo,
        response_format=VisualizacaoResultado,
    )
