from app.agents.prompts.reutilizaveis import (
    CONTEXTO_INSTRUCAO,
    GLOSSARIO_INSTRUCAO,
    GESTOR_INSTRUCAO,
    SOLICITANTE_INSTRUCAO,
    TECNICO_INSTRUCAO,
    ADMINISTRADOR_INSTRUCAO,
    MAPEAMENTO_CATEGORIA_PROBLEMA_INSTRUCAO,
)
from app.agents.prompts.especialistas import (
    AJUDA_GERAL_INSTRUCAO,
    AJUDA_GERAL_INSTRUCAO_SOLICITANTE_TECNICO,
    AJUDA_GERAL_INSTRUCAO_TECNICO_GESTOR,
    AJUDA_GERAL_INSTRUCAO_GESTOR,
    INDICADORES_INSTRUCAO,
    FAQ_INSTRUCAO,
    RETORNO_USUARIO_INSTRUCAO,
    SOLICITACOES_INSTRUCAO,
    VISUALIZACOES_INSTRUCAO,
)

def construir_ajuda_geral_solicitante() -> str:
    """Combina blocos de instrução de ajuda geral solicitante. Usado pelo fluxo de prompts."""
    return "\n".join([
        CONTEXTO_INSTRUCAO, SOLICITANTE_INSTRUCAO, AJUDA_GERAL_INSTRUCAO,
        AJUDA_GERAL_INSTRUCAO_SOLICITANTE_TECNICO,
    ])


def construir_ajuda_geral_tecnico() -> str:
    """Combina blocos de instrução de ajuda geral tecnico. Usado pelo fluxo de prompts."""
    return "\n".join([
        CONTEXTO_INSTRUCAO, TECNICO_INSTRUCAO, AJUDA_GERAL_INSTRUCAO,
        AJUDA_GERAL_INSTRUCAO_SOLICITANTE_TECNICO, AJUDA_GERAL_INSTRUCAO_TECNICO_GESTOR,
    ])


def construir_ajuda_geral_gestor() -> str:
    """Combina blocos de instrução de ajuda geral gestor. Usado pelo fluxo de prompts."""
    return "\n".join([
        CONTEXTO_INSTRUCAO, GESTOR_INSTRUCAO, AJUDA_GERAL_INSTRUCAO,
        AJUDA_GERAL_INSTRUCAO_TECNICO_GESTOR, AJUDA_GERAL_INSTRUCAO_GESTOR,
    ])

def construir_ajuda_geral_administrador() -> str:
    """Combina blocos de instrução de ajuda geral administrador. Usado pelo fluxo de prompts."""
    return "\n".join([
        CONTEXTO_INSTRUCAO, ADMINISTRADOR_INSTRUCAO, AJUDA_GERAL_INSTRUCAO,
        AJUDA_GERAL_INSTRUCAO_SOLICITANTE_TECNICO, AJUDA_GERAL_INSTRUCAO_TECNICO_GESTOR,
    ])

def construir_retorno_usuario() -> str:
    """Combina blocos de instrução de retorno usuario. Usado pelo fluxo de prompts."""
    return (
        CONTEXTO_INSTRUCAO + "\n" +
        GLOSSARIO_INSTRUCAO   +"\n"+
        RETORNO_USUARIO_INSTRUCAO
    )

def construir_faq_solicitante() -> str:
    """Combina blocos de instrução de faq solicitante. Usado pelo fluxo de prompts."""
    return (
        CONTEXTO_INSTRUCAO + "\n" +
        SOLICITANTE_INSTRUCAO +"\n"+
        FAQ_INSTRUCAO
    )

def construir_faq_tecnico() -> str:
    """Combina blocos de instrução de faq tecnico. Usado pelo fluxo de prompts."""
    return (
        CONTEXTO_INSTRUCAO + "\n" +
        TECNICO_INSTRUCAO     +"\n"+
        FAQ_INSTRUCAO
    )

def construir_faq_gestor() -> str:
    """Combina blocos de instrução de faq gestor. Usado pelo fluxo de prompts."""
    return (
        CONTEXTO_INSTRUCAO + "\n" +
        GESTOR_INSTRUCAO      +"\n"+
        FAQ_INSTRUCAO
    )

def construir_faq_administrador() -> str:
    """Combina blocos de instrução de faq administrador. Usado pelo fluxo de prompts."""
    return (
        CONTEXTO_INSTRUCAO + "\n" +
        ADMINISTRADOR_INSTRUCAO +"\n"+
        FAQ_INSTRUCAO
    )


def construir_solicitacoes_solicitante() -> str:
    """Combina blocos de instrução de solicitacoes solicitante. Usado pelo fluxo de prompts."""
    return "\n".join([
        CONTEXTO_INSTRUCAO,
        GLOSSARIO_INSTRUCAO,
        SOLICITANTE_INSTRUCAO,
        SOLICITACOES_INSTRUCAO,
        MAPEAMENTO_CATEGORIA_PROBLEMA_INSTRUCAO,
    ])


def construir_solicitacoes_tecnico() -> str:
    """Combina blocos de instrução de solicitacoes tecnico. Usado pelo fluxo de prompts."""
    return "\n".join([
        CONTEXTO_INSTRUCAO,
        GLOSSARIO_INSTRUCAO,
        TECNICO_INSTRUCAO,
        SOLICITACOES_INSTRUCAO,
        MAPEAMENTO_CATEGORIA_PROBLEMA_INSTRUCAO,
    ])


def construir_solicitacoes_gestor() -> str:
    """Combina blocos de instrução de solicitacoes gestor. Usado pelo fluxo de prompts."""
    return "\n".join([
        CONTEXTO_INSTRUCAO,
        GLOSSARIO_INSTRUCAO,
        GESTOR_INSTRUCAO,
        SOLICITACOES_INSTRUCAO,
        MAPEAMENTO_CATEGORIA_PROBLEMA_INSTRUCAO,
    ])

def construir_solicitacoes_administrador() -> str:
    """Combina blocos de instrução de solicitacoes administrador. Usado pelo fluxo de prompts."""
    return "\n".join([
        CONTEXTO_INSTRUCAO,
        GLOSSARIO_INSTRUCAO,
        ADMINISTRADOR_INSTRUCAO,
        SOLICITACOES_INSTRUCAO,
        MAPEAMENTO_CATEGORIA_PROBLEMA_INSTRUCAO,
    ])


def construir_indicadores_gestor() -> str:
    """Combina blocos de instrução de indicadores gestor. Usado pelo fluxo de prompts."""
    return "\n".join([
        CONTEXTO_INSTRUCAO,
        GLOSSARIO_INSTRUCAO,
        GESTOR_INSTRUCAO,
        INDICADORES_INSTRUCAO,
    ])


def construir_indicadores_administrador() -> str:
    """Combina blocos de instrução de indicadores administrador. Usado pelo fluxo de prompts."""
    return "\n".join([
        CONTEXTO_INSTRUCAO,
        GLOSSARIO_INSTRUCAO,
        ADMINISTRADOR_INSTRUCAO,
        INDICADORES_INSTRUCAO,
    ])


def construir_visualizacoes_gestor() -> str:
    """Combina blocos de instrução de visualizacoes gestor. Usado pelo fluxo de prompts."""
    return "\n".join([
        CONTEXTO_INSTRUCAO,
        GLOSSARIO_INSTRUCAO,
        GESTOR_INSTRUCAO,
        VISUALIZACOES_INSTRUCAO,
    ])


def construir_visualizacoes_administrador() -> str:
    """Combina blocos de instrução de visualizacoes administrador. Usado pelo fluxo de prompts."""
    return "\n".join([
        CONTEXTO_INSTRUCAO,
        GLOSSARIO_INSTRUCAO,
        ADMINISTRADOR_INSTRUCAO,
        VISUALIZACOES_INSTRUCAO,
    ])
