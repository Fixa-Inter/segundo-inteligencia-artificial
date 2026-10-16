from langchain.agents import create_agent
from langchain.agents.middleware import ModelFallbackMiddleware

from app.agents.agentsResult import SolicitacaoOcorrenciaResultado
from app.tools.solicitacoes import buscar_opcoes_solicitacao
from app.tools.solicitacoes import listar_minhas_solicitacoes
from app.tools.solicitacoes import (
    criar_solicitacao,
    salvar_rascunho_solicitacao,
)
from app.tools.solicitacoes import listar_todas_solicitacoes_pendentes
from app.tools.ordensServico import listar_minhas_ordens_servico
from app.tools.ordensServico import listar_todas_ordens_servico
from app.tools.ordensServico import buscar_ordem_servico
from app.tools.tecnicos import buscar_tecnicos_disponiveis
from app.tools.ocorrencias import listar_minhas_ocorrencias
from app.tools.ocorrencias import buscar_opcoes_ocorrencia
from app.tools.ocorrencias import criar_ocorrencia, salvar_rascunho_ocorrencia
from app.tools.memoria import buscar_historico
from app.graph import ContextoGrafo


def criar_agente_solicitacoes(modelo, instrucao: str, modelo_alternativo=None, *, gestor: bool = False, tecnico: bool = False, solicitante:bool = False):
    ferramentas = [buscar_opcoes_solicitacao, buscar_historico]
    if gestor:
        ferramentas.append(listar_todas_solicitacoes_pendentes)
        ferramentas.append(listar_todas_ordens_servico)
        ferramentas.append(buscar_ordem_servico)
        ferramentas.append(buscar_tecnicos_disponiveis)
    if gestor or tecnico:
        ferramentas.append(listar_minhas_ordens_servico)
        if tecnico:
            ferramentas.append(buscar_ordem_servico)
        ferramentas.append(listar_minhas_ocorrencias)
        ferramentas.extend([buscar_opcoes_ocorrencia, salvar_rascunho_ocorrencia, criar_ocorrencia])
    if tecnico or solicitante:
        ferramentas.append(salvar_rascunho_solicitacao)
        ferramentas.append(criar_solicitacao)
        ferramentas.append(listar_minhas_solicitacoes)
    return create_agent(
        model=modelo,
        system_prompt=instrucao,
        tools=ferramentas,
        response_format=SolicitacaoOcorrenciaResultado,
        context_schema=ContextoGrafo,
        middleware=[ModelFallbackMiddleware(modelo_alternativo)] if modelo_alternativo is not None else [],
    )
