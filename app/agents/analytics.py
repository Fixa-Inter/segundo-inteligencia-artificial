from langchain.agents import create_agent

from app.agents.agentsResult import AnalyticsResultado


def criar_agente_analytics(model, prompt: str, tools=None):
    return create_agent(
        model=model,
        system_prompt=prompt,
        tools=tools or [],
        response_format=AnalyticsResultado,
    )
