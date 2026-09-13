from langchain.agents import create_agent

from app.agents.llms import llm_especialista, llm_rapido, llm_gemini, llm_groq
from app.agents.solicitacoes import criar_agente_solicitacoes
from app.agents.prompts.construtor import (
    construir_analytics_gestor,
    construir_faq_gestor,
    construir_faq_solicitante,
    construir_faq_tecnico,
    construir_feedback,
    construir_juiz_gestor,
    construir_juiz_solicitante,
    construir_juiz_tecnico,
    construir_solicitacoes_gestor,
    construir_solicitacoes_solicitante,
    construir_solicitacoes_tecnico,
    construir_visualizacoes_gestor,
)
from app.agents.agentsResult import (
    AnalyticsResultado,
    FAQResultado,
    FeedbackResultado,
    JuizResultado,
    SolicitacaoOcorrenciaResultado,
    VisualizacaoResultado,
)

faq_solicitante = create_agent(
    system_prompt=construir_faq_solicitante(),
    model=llm_especialista,
    response_format=FAQResultado,
)

faq_tecnico = create_agent(
    system_prompt=construir_faq_tecnico(),
    model=llm_especialista,
    response_format=FAQResultado,
)

faq_gestor = create_agent(
    system_prompt=construir_faq_gestor(),
    model=llm_especialista,
    response_format=FAQResultado,
)

feedback = create_agent(
    system_prompt=construir_feedback(),
    model=llm_rapido,
    response_format=FeedbackResultado,
)

juiz_solicitante = create_agent(
    system_prompt=construir_juiz_solicitante(),
    model=llm_especialista,
    response_format=JuizResultado,
)

juiz_tecnico = create_agent(
    system_prompt=construir_juiz_tecnico(),
    model=llm_especialista,
    response_format=JuizResultado,
)

juiz_gestor = create_agent(
    system_prompt=construir_juiz_gestor(),
    model=llm_especialista,
    response_format=JuizResultado,
)

solicitacoes_solicitante = criar_agente_solicitacoes(
    prompt=construir_solicitacoes_solicitante(),
    model=llm_gemini, fallback=llm_groq,
)

solicitacoes_tecnico = criar_agente_solicitacoes(
    prompt=construir_solicitacoes_tecnico(),
    model=llm_gemini, fallback=llm_groq,
)

solicitacoes_gestor = criar_agente_solicitacoes(
    prompt=construir_solicitacoes_gestor(),
    model=llm_gemini, fallback=llm_groq,
)

analytics_gestor = create_agent(
    system_prompt=construir_analytics_gestor(),
    model=llm_especialista,
    response_format=AnalyticsResultado,
)

visualizacoes_gestor = create_agent(
    system_prompt=construir_visualizacoes_gestor(),
    model=llm_especialista,
    response_format=VisualizacaoResultado,
)
