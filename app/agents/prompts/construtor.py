from app.agents.prompts.reutilizaveis import CONTEXTO_INSTRUCAO, GLOSSARIO_INSTRUCAO, GESTOR_INSTRUCAO, SOLICITANTE_INSTRUCAO, TECNICO_INSTRUCAO
from app.agents.prompts.reutilizaveis import MAPEAMENTO_CATEGORIA_PROBLEMA_INSTRUCAO
from app.agents.prompts.especialistas import (
    AJUDA_GERAL_INSTRUCAO,
    AJUDA_GERAL_INSTRUCAO_TECNICO_GESTOR,
    INDICADORES_INSTRUCAO,
    FAQ_INSTRUCAO,
    RETORNO_USUARIO_INSTRUCAO,
    JUIZ_INSTRUCAO,
    SOLICITACOES_INSTRUCAO,
    VISUALIZACOES_INSTRUCAO,
)


def construir_ajuda_geral_solicitante() -> str:
    return "\n".join([CONTEXTO_INSTRUCAO, SOLICITANTE_INSTRUCAO, AJUDA_GERAL_INSTRUCAO])


def construir_ajuda_geral_tecnico() -> str:
    return "\n".join([
        CONTEXTO_INSTRUCAO, TECNICO_INSTRUCAO, AJUDA_GERAL_INSTRUCAO,
        AJUDA_GERAL_INSTRUCAO_TECNICO_GESTOR,
    ])


def construir_ajuda_geral_gestor() -> str:
    return "\n".join([
        CONTEXTO_INSTRUCAO, GESTOR_INSTRUCAO, AJUDA_GERAL_INSTRUCAO,
        AJUDA_GERAL_INSTRUCAO_TECNICO_GESTOR,
    ])

def construir_juiz_solicitante() -> str:
    return (
        CONTEXTO_INSTRUCAO     +"\n"+
        GLOSSARIO_INSTRUCAO    +"\n"+
        SOLICITANTE_INSTRUCAO  +"\n"+
        JUIZ_INSTRUCAO
    )

def construir_juiz_tecnico() -> str:
    return (
        CONTEXTO_INSTRUCAO    +"\n"+
        GLOSSARIO_INSTRUCAO   +"\n"+
        TECNICO_INSTRUCAO     +"\n"+
        JUIZ_INSTRUCAO
    )

def construir_juiz_gestor() -> str:
    return (
        CONTEXTO_INSTRUCAO    +"\n"+
        GLOSSARIO_INSTRUCAO   +"\n"+
        GESTOR_INSTRUCAO      +"\n"+
        JUIZ_INSTRUCAO
    )

def construir_retorno_usuario() -> str:
    return (
        GLOSSARIO_INSTRUCAO   +"\n"+
        RETORNO_USUARIO_INSTRUCAO
    )

def construir_faq_solicitante() -> str:
    return (
        SOLICITANTE_INSTRUCAO +"\n"+
        FAQ_INSTRUCAO
    )

def construir_faq_tecnico() -> str:
    return (
        TECNICO_INSTRUCAO     +"\n"+
        FAQ_INSTRUCAO
    )

def construir_faq_gestor() -> str:
    return (
        GESTOR_INSTRUCAO      +"\n"+
        FAQ_INSTRUCAO
    )


def construir_solicitacoes_solicitante() -> str:
    return "\n".join([
        CONTEXTO_INSTRUCAO,
        GLOSSARIO_INSTRUCAO,
        SOLICITANTE_INSTRUCAO,
        SOLICITACOES_INSTRUCAO,
        MAPEAMENTO_CATEGORIA_PROBLEMA_INSTRUCAO,
    ])


def construir_solicitacoes_tecnico() -> str:
    return "\n".join([
        CONTEXTO_INSTRUCAO,
        GLOSSARIO_INSTRUCAO,
        TECNICO_INSTRUCAO,
        SOLICITACOES_INSTRUCAO,
        MAPEAMENTO_CATEGORIA_PROBLEMA_INSTRUCAO,
    ])


def construir_solicitacoes_gestor() -> str:
    return "\n".join([
        CONTEXTO_INSTRUCAO,
        GLOSSARIO_INSTRUCAO,
        GESTOR_INSTRUCAO,
        SOLICITACOES_INSTRUCAO,
        MAPEAMENTO_CATEGORIA_PROBLEMA_INSTRUCAO,
    ])


def construir_indicadores_gestor() -> str:
    return "\n".join([
        CONTEXTO_INSTRUCAO,
        GLOSSARIO_INSTRUCAO,
        GESTOR_INSTRUCAO,
        INDICADORES_INSTRUCAO,
    ])


def construir_visualizacoes_gestor() -> str:
    return "\n".join([
        CONTEXTO_INSTRUCAO,
        GLOSSARIO_INSTRUCAO,
        GESTOR_INSTRUCAO,
        VISUALIZACOES_INSTRUCAO,
    ])

