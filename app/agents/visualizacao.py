from langchain.agents import create_agent
from app.graph import ContextoGrafo
from app.tools.memoria import buscar_historico

from app.agents.agentsResult import VisualizacaoResultado


def criar_agente_visualizacao(modelo, instrucao: str, ferramentas=None):
    return create_agent(
        model=modelo,
        system_prompt=instrucao,
        tools=[*(ferramentas or []), buscar_historico],
        context_schema=ContextoGrafo,
        response_format=VisualizacaoResultado,
    )
