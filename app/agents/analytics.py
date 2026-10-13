from langchain.agents import create_agent
from app.graph.context import GraphContext
from app.tools.memoria.buscar_historico import buscar_historico

from app.agents.agentsResult import AnalyticsResultado


def criar_agente_analytics(model, prompt: str, tools=None):
    return create_agent(
        model=model,
        system_prompt=prompt,
        tools=[*(tools or []), buscar_historico],
        context_schema=GraphContext,
        response_format=AnalyticsResultado,
    )
