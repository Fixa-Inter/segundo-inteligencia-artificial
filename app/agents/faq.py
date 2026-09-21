from langchain.agents import create_agent
from langchain.agents.middleware import ModelFallbackMiddleware

from app.agents.agentsResult.FAQResultado import (
    FAQResultado,
)
from app.graph.context import GraphContext
from app.tools.faq.buscar import buscar_faq

def criar_agente_faq(
    model,
    prompt: str,
    fallback=None,
):
    middleware = (
        [ModelFallbackMiddleware(fallback)]
        if fallback is not None
        else []
    )

    return create_agent(
        model=model,
        system_prompt=prompt,
        tools=[buscar_faq],
        response_format=FAQResultado,
        context_schema=GraphContext,
        middleware=middleware,
    )