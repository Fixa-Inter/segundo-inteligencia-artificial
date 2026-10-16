from langchain.agents import create_agent
from langchain.agents.middleware import ModelFallbackMiddleware

from app.agents.agentsResult import (
    FAQResultado,
)
from app.graph import ContextoGrafo
from app.tools.faq import buscar_faq
from app.tools.memoria import buscar_historico

def criar_agente_faq(
    modelo,
    instrucao: str,
    modelo_alternativo=None,
):
    middleware = (
        [ModelFallbackMiddleware(modelo_alternativo)]
        if modelo_alternativo is not None
        else []
    )

    return create_agent(
        model=modelo,
        system_prompt=instrucao,
        tools=[buscar_faq, buscar_historico],
        response_format=FAQResultado,
        context_schema=ContextoGrafo,
        middleware=middleware,
    )