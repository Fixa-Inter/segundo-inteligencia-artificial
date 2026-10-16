from langchain.agents import create_agent
from app.graph import ContextoGrafo
from app.tools.memoria import buscar_historico

from app.agents.agentsResult import IndicadoresResultado


def criar_agente_indicadores(modelo, instrucao: str, ferramentas=None):
    return create_agent(
        model=modelo,
        system_prompt=instrucao,
        tools=[*(ferramentas or []), buscar_historico],
        context_schema=ContextoGrafo,
        response_format=IndicadoresResultado,
    )
