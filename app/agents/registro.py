from app.agents import (
    criar_agente_faq,
    criar_agente_solicitacoes,
    criar_agente_ajuda_geral,
    criar_agente_indicadores,
    criar_agente_visualizacao,
    criar_agente_retorno_usuario,
    llm_especialista,
    llm_luna,
)
from app.tools.feedback import criar_nome_feedback
from app.agents.prompts import (
    construir_ajuda_geral_administrador,
    construir_ajuda_geral_gestor,
    construir_ajuda_geral_solicitante,
    construir_ajuda_geral_tecnico,
    construir_faq_administrador,
    construir_indicadores_gestor,
    construir_indicadores_administrador,
    construir_faq_gestor,
    construir_faq_solicitante,
    construir_faq_tecnico,
    construir_retorno_usuario,
    construir_solicitacoes_gestor,
    construir_solicitacoes_solicitante,
    construir_solicitacoes_tecnico,
    construir_solicitacoes_administrador,
    construir_visualizacoes_gestor,
    construir_visualizacoes_administrador,
)

# ajuda_geral_solicitante: Recurso compartilhado de ajuda geral solicitante usado pelas funções deste módulo e pela interface pública.
ajuda_geral_solicitante = criar_agente_ajuda_geral(
    llm_luna, construir_ajuda_geral_solicitante(), perfil="solicitante",
)
# ajuda_geral_tecnico: Recurso compartilhado de ajuda geral tecnico usado pelas funções deste módulo e pela interface pública.
ajuda_geral_tecnico = criar_agente_ajuda_geral(
    llm_luna, construir_ajuda_geral_tecnico(), perfil="tecnico",
)
# ajuda_geral_administrador: Recurso compartilhado de ajuda geral administrador usado pelas funções deste módulo e pela interface pública.
ajuda_geral_administrador = criar_agente_ajuda_geral(
    llm_luna, construir_ajuda_geral_administrador(), perfil="administrador",
)
# ajuda_geral_gestor: Recurso compartilhado de ajuda geral gestor usado pelas funções deste módulo e pela interface pública.
ajuda_geral_gestor = criar_agente_ajuda_geral(
    llm_luna, construir_ajuda_geral_gestor(), perfil="gestor",
)

# faq_solicitante: Recurso compartilhado de faq solicitante usado pelas funções deste módulo e pela interface pública.
faq_solicitante = criar_agente_faq(llm_luna, construir_faq_solicitante())
# faq_tecnico: Recurso compartilhado de faq tecnico usado pelas funções deste módulo e pela interface pública.
faq_tecnico = criar_agente_faq(llm_luna, construir_faq_tecnico())
# faq_administrador: Recurso compartilhado de faq administrador usado pelas funções deste módulo e pela interface pública.
faq_administrador = criar_agente_faq(llm_luna, construir_faq_administrador())
# faq_gestor: Recurso compartilhado de faq gestor usado pelas funções deste módulo e pela interface pública.
faq_gestor = criar_agente_faq(llm_luna, construir_faq_gestor())

# solicitacoes_solicitante: Recurso compartilhado de solicitacoes solicitante usado pelas funções deste módulo e pela interface pública.
solicitacoes_solicitante = criar_agente_solicitacoes(modelo=llm_luna, instrucao=construir_solicitacoes_solicitante(), solicitante=True)
# solicitacoes_tecnico: Recurso compartilhado de solicitacoes tecnico usado pelas funções deste módulo e pela interface pública.
solicitacoes_tecnico = criar_agente_solicitacoes(modelo=llm_luna, instrucao=construir_solicitacoes_tecnico(), tecnico=True)
# solicitacoes_administrador: Recurso compartilhado de solicitacoes administrador usado pelas funções deste módulo e pela interface pública.
solicitacoes_administrador = criar_agente_solicitacoes(
    modelo=llm_luna, instrucao=construir_solicitacoes_administrador(), gestor=True,
)
# solicitacoes_gestor: Recurso compartilhado de solicitacoes gestor usado pelas funções deste módulo e pela interface pública.
solicitacoes_gestor = criar_agente_solicitacoes(modelo=llm_luna, instrucao=construir_solicitacoes_gestor(), gestor=True)

# indicadores_gestor: Recurso compartilhado de indicadores gestor usado pelas funções deste módulo e pela interface pública.
indicadores_gestor = criar_agente_indicadores(llm_especialista, construir_indicadores_gestor())
# indicadores_administrador: Recurso compartilhado de indicadores administrador usado pelas funções deste módulo e pela interface pública.
indicadores_administrador = criar_agente_indicadores(llm_especialista, construir_indicadores_administrador())
# visualizacoes_gestor: Recurso compartilhado de visualizacoes gestor usado pelas funções deste módulo e pela interface pública.
visualizacoes_gestor = criar_agente_visualizacao(llm_especialista, construir_visualizacoes_gestor())
# visualizacoes_administrador: Recurso compartilhado de visualizacoes administrador usado pelas funções deste módulo e pela interface pública.
visualizacoes_administrador = criar_agente_visualizacao(llm_especialista, construir_visualizacoes_administrador())
# feedback: Recurso compartilhado de feedback usado pelas funções deste módulo e pela interface pública.
feedback = criar_agente_retorno_usuario(
    llm_luna,
    construir_retorno_usuario(),
    ferramentas=[criar_nome_feedback],
)
# AGENTES_POR_PERFIL: Registro explícito de recursos disponíveis para seleção por funcionalidade/perfil.
AGENTES_POR_PERFIL = {
    "ajuda_geral": {
        "solicitante": ajuda_geral_solicitante,
        "tecnico": ajuda_geral_tecnico,
        "gestor": ajuda_geral_gestor,
        "administrador": ajuda_geral_administrador,
    },
    "faq": {
        "solicitante": faq_solicitante,
        "tecnico": faq_tecnico,
        "gestor": faq_gestor,
        "administrador": faq_administrador,
    },
    "solicitacao": {
        "solicitante": solicitacoes_solicitante,
        "tecnico": solicitacoes_tecnico,
        "gestor": solicitacoes_gestor,
        "administrador": solicitacoes_administrador,
    },
    "analytics": {"gestor": indicadores_gestor, "administrador": indicadores_administrador},
    "visualizacao": {"gestor": visualizacoes_gestor, "administrador": visualizacoes_administrador},
}


def selecionar_agente(tipo: str, perfil: str, candidatos=None):
    """Retorna o agente compativel com a funcionalidade e o perfil informado."""
    agentes = candidatos if candidatos is not None else AGENTES_POR_PERFIL.get(tipo, {})
    return agentes.get(perfil)
