from langchain.agents import create_agent
from langchain.agents.middleware import ModelFallbackMiddleware

from app.agents.agentsResult.SolicitacaoOcorrenciaResultado import SolicitacaoOcorrenciaResultado
from app.tools.solicitacoes.buscarOpcoes import buscar_opcoes_solicitacao
from app.tools.solicitacoes.criarSolicitacao import criar_solicitacao


def criar_agente_solicitacoes(model, prompt: str, fallback=None):
    return create_agent(
        model=model, system_prompt=prompt,
        tools=[buscar_opcoes_solicitacao, criar_solicitacao],
        response_format=SolicitacaoOcorrenciaResultado,
        middleware=[ModelFallbackMiddleware(fallback)] if fallback is not None else [],
    )
