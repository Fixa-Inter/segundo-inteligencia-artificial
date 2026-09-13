from app.agents.prompts.reutilizaveis import CONTEXTO_PROMPT, CONTEXTO_TEMPORAL, GLOSSARIO_PROMPT, GESTOR_PROMPT, SOLICITANTE_PROMPT, TECNICO_PROMPT
from app.agents.prompts.especialistas import (
    ANALYTICS_PROMPT,
    FAQ_PROMPT,
    FEEDBACK_PROMPT,
    JUIZ_PROMPT,
    SOLICITACOES_PROMPT,
    VISUALIZACOES_PROMPT,
)

def construir_juiz_solicitante() -> str:
    return (
        CONTEXTO_PROMPT     +"\n"+
        CONTEXTO_TEMPORAL   +"\n"+
        GLOSSARIO_PROMPT    +"\n"+
        SOLICITANTE_PROMPT  +"\n"+
        JUIZ_PROMPT
    )

def construir_juiz_tecnico() -> str:
    return (
        CONTEXTO_PROMPT    +"\n"+
        CONTEXTO_TEMPORAL  +"\n"+
        GLOSSARIO_PROMPT   +"\n"+
        TECNICO_PROMPT     +"\n"+
        JUIZ_PROMPT
    )

def construir_juiz_gestor() -> str:
    return (
        CONTEXTO_PROMPT    +"\n"+
        CONTEXTO_TEMPORAL  +"\n"+
        GLOSSARIO_PROMPT   +"\n"+
        GESTOR_PROMPT      +"\n"+
        JUIZ_PROMPT
    )

def construir_feedback() -> str:
    return (
        CONTEXTO_TEMPORAL  +"\n"+
        GLOSSARIO_PROMPT   +"\n"+
        FEEDBACK_PROMPT
    )

def construir_faq_solicitante() -> str:
    return (
        SOLICITANTE_PROMPT +"\n"+
        FAQ_PROMPT
    )

def construir_faq_tecnico() -> str:
    return (
        TECNICO_PROMPT     +"\n"+
        FAQ_PROMPT
    )

def construir_faq_gestor() -> str:
    return (
        GESTOR_PROMPT      +"\n"+
        FAQ_PROMPT
    )


def construir_solicitacoes_solicitante() -> str:
    return "\n".join([
        CONTEXTO_PROMPT,
        CONTEXTO_TEMPORAL,
        GLOSSARIO_PROMPT,
        SOLICITANTE_PROMPT,
        SOLICITACOES_PROMPT,
    ])


def construir_solicitacoes_tecnico() -> str:
    return "\n".join([
        CONTEXTO_PROMPT,
        CONTEXTO_TEMPORAL,
        GLOSSARIO_PROMPT,
        TECNICO_PROMPT,
        SOLICITACOES_PROMPT,
    ])


def construir_solicitacoes_gestor() -> str:
    return "\n".join([
        CONTEXTO_PROMPT,
        CONTEXTO_TEMPORAL,
        GLOSSARIO_PROMPT,
        GESTOR_PROMPT,
        SOLICITACOES_PROMPT,
    ])


def construir_analytics_gestor() -> str:
    return "\n".join([
        CONTEXTO_PROMPT,
        CONTEXTO_TEMPORAL,
        GLOSSARIO_PROMPT,
        GESTOR_PROMPT,
        ANALYTICS_PROMPT,
    ])


def construir_visualizacoes_gestor() -> str:
    return "\n".join([
        CONTEXTO_PROMPT,
        CONTEXTO_TEMPORAL,
        GLOSSARIO_PROMPT,
        GESTOR_PROMPT,
        VISUALIZACOES_PROMPT,
    ])

