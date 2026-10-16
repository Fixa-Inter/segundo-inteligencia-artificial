from app.agents.faq import criar_agente_faq
from app.agents.solicitacoes import criar_agente_solicitacoes
from app.agents.ajuda_geral import criar_agente_ajuda_geral
from app.agents.indicadores import criar_agente_indicadores
from app.agents.visualizacao import criar_agente_visualizacao
from app.agents.retorno_usuario import criar_agente_retorno_usuario
from app.tools.feedback import criar_nome_feedback
from app.agents.juiz import criar_agente_juiz
from app.agents.modelos import llm_especialista, llm_luna, llm_groq
from app.agents.prompts.construtor import (
    construir_ajuda_geral_gestor,
    construir_ajuda_geral_solicitante,
    construir_ajuda_geral_tecnico,
    construir_indicadores_gestor,
    construir_faq_gestor,
    construir_faq_solicitante,
    construir_faq_tecnico,
    construir_retorno_usuario,
    construir_solicitacoes_gestor,
    construir_solicitacoes_solicitante,
    construir_solicitacoes_tecnico,
    construir_visualizacoes_gestor,
)

ajuda_geral_solicitante = criar_agente_ajuda_geral(
    llm_luna, construir_ajuda_geral_solicitante(), perfil="solicitante",
)
ajuda_geral_tecnico = criar_agente_ajuda_geral(
    llm_luna, construir_ajuda_geral_tecnico(), perfil="tecnico",
)
ajuda_geral_gestor = criar_agente_ajuda_geral(
    llm_luna, construir_ajuda_geral_gestor(), perfil="gestor",
)

faq_solicitante = criar_agente_faq(llm_luna, construir_faq_solicitante())
faq_tecnico = criar_agente_faq(llm_luna, construir_faq_tecnico())
faq_gestor = criar_agente_faq(llm_luna, construir_faq_gestor())

solicitacoes_solicitante = criar_agente_solicitacoes(modelo=llm_luna, instrucao=construir_solicitacoes_solicitante(), solicitante=True)
solicitacoes_tecnico = criar_agente_solicitacoes(modelo=llm_luna, instrucao=construir_solicitacoes_tecnico(), tecnico=True)
solicitacoes_gestor = criar_agente_solicitacoes(modelo=llm_luna, instrucao=construir_solicitacoes_gestor(), gestor=True)

indicadores_gestor = criar_agente_indicadores(llm_especialista, construir_indicadores_gestor())
visualizacoes_gestor = criar_agente_visualizacao(llm_especialista, construir_visualizacoes_gestor())
feedback = criar_agente_retorno_usuario(
    llm_luna,
    construir_retorno_usuario(),
    ferramentas=[criar_nome_feedback],
)
juiz = criar_agente_juiz(llm_luna, modelo_alternativo=llm_groq)

AGENTES_POR_PERFIL = {
    "ajuda_geral": {
        "solicitante": ajuda_geral_solicitante,
        "tecnico": ajuda_geral_tecnico,
        "gestor": ajuda_geral_gestor,
    },
    "faq": {
        "solicitante": faq_solicitante,
        "tecnico": faq_tecnico,
        "gestor": faq_gestor,
    },
    "solicitacao": {
        "solicitante": solicitacoes_solicitante,
        "tecnico": solicitacoes_tecnico,
        "gestor": solicitacoes_gestor,
    },
    "analytics": {"gestor": indicadores_gestor},
    "visualizacao": {"gestor": visualizacoes_gestor},
}


def selecionar_agente(tipo: str, perfil: str, candidatos=None):
    """Retorna o agente compativel com a funcionalidade e o perfil informado."""
    agentes = candidatos if candidatos is not None else AGENTES_POR_PERFIL.get(tipo, {})
    return agentes.get(perfil)


