from app.agents.faq import criar_agente_faq
from app.agents.solicitacoes import criar_agente_solicitacoes
from app.agents.analytics import criar_agente_analytics
from app.agents.visualizacao import criar_agente_visualizacao
from app.agents.feedback import criar_agente_feedback
from app.agents.juiz import criar_agente_juiz
from app.agents.llms import llm_especialista, llm_rapido, llm_gemini, llm_groq
from app.agents.prompts.construtor import (
    construir_analytics_gestor,
    construir_faq_gestor,
    construir_faq_solicitante,
    construir_faq_tecnico,
    construir_feedback,
    construir_solicitacoes_gestor,
    construir_solicitacoes_solicitante,
    construir_solicitacoes_tecnico,
    construir_visualizacoes_gestor,
)

faq_solicitante = criar_agente_faq(llm_gemini, construir_faq_solicitante())
faq_tecnico = criar_agente_faq(llm_gemini, construir_faq_tecnico())
faq_gestor = criar_agente_faq(llm_gemini, construir_faq_gestor())

solicitacoes_solicitante = criar_agente_solicitacoes(model=llm_gemini, prompt=construir_solicitacoes_solicitante(), solicitante=True)
solicitacoes_tecnico = criar_agente_solicitacoes(model=llm_gemini, prompt=construir_solicitacoes_tecnico(), tecnico=True)
solicitacoes_gestor = criar_agente_solicitacoes(model=llm_gemini, prompt=construir_solicitacoes_gestor(), gestor=True)

analytics_gestor = criar_agente_analytics(llm_especialista, construir_analytics_gestor())
visualizacoes_gestor = criar_agente_visualizacao(llm_especialista, construir_visualizacoes_gestor())
feedback = criar_agente_feedback(llm_rapido, construir_feedback())
juiz = criar_agente_juiz(llm_gemini, fallback=llm_groq)

AGENTES_POR_PERFIL = {
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
    "analytics": {"gestor": analytics_gestor},
    "visualizacao": {"gestor": visualizacoes_gestor},
}


def selecionar_agente(tipo: str, perfil: str, candidatos=None):
    """Retorna o agente compativel com a funcionalidade e o perfil informado."""
    agentes = candidatos if candidatos is not None else AGENTES_POR_PERFIL.get(tipo, {})
    return agentes.get(perfil)


