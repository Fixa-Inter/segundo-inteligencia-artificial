from .reutilizaveis import CONTEXTO_PROMPT, CONTEXTO_TEMPORAL, GLOSSARIO_PROMPT, GESTOR_PROMPT, SOLICITANTE_PROMPT, TECNICO_PROMPT
from .especialistas import JUIZ_PROMPT, FEEDBACK_PROMPT, FAQ_PROMPT

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
        TECNICO_PROMPT +"\n"+
        FAQ_PROMPT
    )

def construir_faq_gestor() -> str:
    return (
        GESTOR_PROMPT +"\n"+
        FAQ_PROMPT
    )

