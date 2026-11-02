from langchain.agents import create_agent
from langchain.agents.middleware import ModelFallbackMiddleware

from app.agents.agentsResult import SolicitacaoOcorrenciaResultado
from app.tools.solicitacoes import buscar_opcoes_solicitacao
from app.tools.solicitacoes import (
    criar_solicitacao,
    salvar_rascunho_solicitacao,
)
from app.tools.ocorrencias import buscar_opcoes_ocorrencia
from app.tools.ocorrencias import criar_ocorrencia, salvar_rascunho_ocorrencia
from app.tools.memoria import buscar_historico
from app.tools.eventos import buscar_opcoes_evento, salvar_rascunho_evento, criar_evento
from app.graph import ContextoGrafo


def criar_agente_solicitacoes(modelo, instrucao: str, modelo_alternativo=None, *, gestor: bool = False, tecnico: bool = False, solicitante:bool = False):
    ferramentas = [buscar_opcoes_solicitacao, buscar_historico]
    if gestor or tecnico:
        ferramentas.extend([buscar_opcoes_ocorrencia, salvar_rascunho_ocorrencia, criar_ocorrencia])
    if gestor:
        ferramentas.extend([buscar_opcoes_evento, salvar_rascunho_evento, criar_evento])
    if tecnico or solicitante:
        ferramentas.append(salvar_rascunho_solicitacao)
        ferramentas.append(criar_solicitacao)
    return create_agent(
        model=modelo,
        system_prompt=instrucao,
        tools=ferramentas,
        response_format=SolicitacaoOcorrenciaResultado,
        context_schema=ContextoGrafo,
        middleware=[ModelFallbackMiddleware(modelo_alternativo)] if modelo_alternativo is not None else [],
    )
