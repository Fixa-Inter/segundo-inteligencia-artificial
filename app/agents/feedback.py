from langchain.agents import create_agent
from app.graph.context import GraphContext
from app.tools.memoria.buscar_historico import buscar_historico

from app.agents.agentsResult import FeedbackResultado


def criar_agente_feedback(model, prompt: str, tools=None):
    return create_agent(
        model=model,
        system_prompt=prompt,
        tools=[*(tools or []), buscar_historico],
        context_schema=GraphContext,
        response_format=FeedbackResultado,
    )
