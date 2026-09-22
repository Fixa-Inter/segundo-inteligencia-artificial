from langchain.agents import create_agent
from langchain.agents.middleware import ModelFallbackMiddleware

from app.agents.agentsResult.SolicitacaoOcorrenciaResultado import SolicitacaoOcorrenciaResultado
from app.tools.solicitacoes.buscarOpcoes import buscar_opcoes_solicitacao
from app.tools.solicitacoes.listarMinhasSolicitacoes import listar_minhas_solicitacoes
from app.tools.solicitacoes.criarSolicitacao import criar_solicitacao
from app.tools.solicitacoes.listarTodasSolicitacoesPendentes import listar_todas_solicitacoes_pendentes
from app.tools.ordensServico.listarMinhasOrdensServico import listar_minhas_ordens_servico
from app.tools.ordensServico.listarTodasOrdensServico import listar_todas_ordens_servico
from app.tools.ocorrencias.listarMinhasOcorrencias import listar_minhas_ocorrencias
from app.tools.ocorrencias.buscarOpcoesOcorrencia import buscar_opcoes_ocorrencia
from app.tools.ocorrencias.criarOcorrencia import criar_ocorrencia
from app.graph.context import GraphContext


def criar_agente_solicitacoes(model, prompt: str, fallback=None, *, gestor: bool = False, tecnico: bool = False):
    ferramentas = [buscar_opcoes_solicitacao, criar_solicitacao, listar_minhas_solicitacoes]
    if gestor:
        ferramentas.append(listar_todas_solicitacoes_pendentes)
        ferramentas.append(listar_todas_ordens_servico)
    if gestor or tecnico:
        ferramentas.append(listar_minhas_ordens_servico)
        ferramentas.append(listar_minhas_ocorrencias)
        ferramentas.extend([buscar_opcoes_ocorrencia, criar_ocorrencia])
    return create_agent(
        model=model, system_prompt=prompt,
        tools=ferramentas,
        response_format=SolicitacaoOcorrenciaResultado,
        context_schema=GraphContext,
        middleware=[ModelFallbackMiddleware(fallback)] if fallback is not None else [],
    )
