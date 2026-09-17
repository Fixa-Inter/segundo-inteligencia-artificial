from langchain.agents import create_agent
from langchain.agents.middleware import ModelFallbackMiddleware

from app.agents.agentsResult.SolicitacaoOcorrenciaResultado import SolicitacaoOcorrenciaResultado
from app.tools.faq import buscar


def criar_agente_faq(model, prompt: str, fallback=None, *, gestor: bool = False, tecnico: bool = False):
    ferramentas = [buscar]

    return create_agent(
        model=model, system_prompt=prompt,
        tools=ferramentas,
        response_format=SolicitacaoOcorrenciaResultado,
        middleware=[ModelFallbackMiddleware(fallback)] if fallback is not None else [],
    )