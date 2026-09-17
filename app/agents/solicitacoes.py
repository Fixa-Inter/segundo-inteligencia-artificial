from langchain.agents import create_agent
from langchain.agents.middleware import ModelFallbackMiddleware

from app.agents.agentsResult.SolicitacaoOcorrenciaResultado import SolicitacaoOcorrenciaResultado
from app.tools.solicitacoes.buscarOpcoes import buscar_opcoes_solicitacao
from app.tools.solicitacoes.listarMinhasSolicitacoes import listar_minhas_solicitacoes
from app.tools.solicitacoes.criarSolicitacao import criar_solicitacao
from app.tools.solicitacoes.listarTodasSolicitacoesPendentes import buscar_todas_solicitacoes_pendentes
from app.tools.ordensServico.listarMinhasOrdensServico import listar_minhas_ordens_servico


def criar_agente_solicitacoes(model, prompt: str, fallback=None, *, gestor: bool = False, tecnico: bool = False):
    ferramentas = [buscar_opcoes_solicitacao, criar_solicitacao, listar_minhas_solicitacoes]
    if gestor:
        ferramentas.append(buscar_todas_solicitacoes_pendentes)
    if gestor or tecnico:
        ferramentas.append(listar_minhas_ordens_servico)
    return create_agent(
        model=model, system_prompt=prompt,
        tools=ferramentas,
        response_format=SolicitacaoOcorrenciaResultado,
        middleware=[ModelFallbackMiddleware(fallback)] if fallback is not None else [],
    )
