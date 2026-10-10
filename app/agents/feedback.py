from langchain.agents import create_agent

from app.agents.agentsResult import FeedbackResultado


def criar_agente_feedback(model, prompt: str, tools=None):
    return create_agent(
        model=model,
        system_prompt=prompt,
        tools=tools or [],
        response_format=FeedbackResultado,
    )
