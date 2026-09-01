from .prompts import construtor
from .llms import llm_especialista, llm_rapido
from langchain.agents import create_agent

faq_solicitante = create_agent(
    system_prompt=construtor.construir_faq_solicitante
    ,model=llm_especialista
)

faq_tecnico = create_agent(
    system_prompt=construtor.construir_faq_tecnico
    ,model=llm_especialista
)

faq_gestor = create_agent(
    system_prompt=construtor.construir_faq_gestor
    ,model=llm_especialista
)

feedback = create_agent(
    system_prompt=construtor.construir_feedback
    ,model=llm_rapido
)

juiz_solicitante = create_agent(
    system_prompt=construtor.construir_faq_tecnico
    ,model=llm_especialista
)

juiz_tecnico = create_agent(
    system_prompt=construtor.construir_juiz_tecnico
    ,model=llm_especialista
)

juiz_gestor = create_agent(
    system_prompt=construtor.construir_juiz_gestor
    ,model=llm_especialista
)