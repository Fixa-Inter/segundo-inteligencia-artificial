"""Interface pública de app/agents; recursos carregados sob demanda."""

from app.core.interfaces import resolver_exportacao as _resolver_exportacao

# Cada nome aponta para seu proprietário; importar o pacote não inicializa clientes/agentes.
_EXPORTACOES = {
    'AGENTES_POR_PERFIL': ('.registro', 'AGENTES_POR_PERFIL'),
    'CRITERIOS_EMOCAO': ('.emocoes', 'CRITERIOS_EMOCAO'),
    'CRITERIOS_MOTIVO': ('.juiz', 'CRITERIOS_MOTIVO'),
    'CRITERIOS_VEREDITO': ('.juiz', 'CRITERIOS_VEREDITO'),
    'DecisaoRoteamento': ('.orquestrador', 'DecisaoRoteamento'),
    'FEEDBACK_MOTIVO': ('.juiz', 'FEEDBACK_MOTIVO'),
    'LimiteConsultasVisualizacao': ('.visualizacao', 'LimiteConsultasVisualizacao'),
    'POLITICAS_PERFIL': ('.juiz', 'POLITICAS_PERFIL'),
    'PROMPT_CLASSIFICACAO': ('.emocoes', 'PROMPT_CLASSIFICACAO'),
    'RespostaRevisada': ('.juiz', 'RespostaRevisada'),
    'TABELAS_LISTAGEM': ('.juiz', 'TABELAS_LISTAGEM'),
    'TEMPO_LIMITE_CLASSIFICACAO': ('.emocoes', 'TEMPO_LIMITE_CLASSIFICACAO'),
    'agentsResult': ('.agentsResult', None),
    'ajuda_geral_administrador': ('.registro', 'ajuda_geral_administrador'),
    'ajuda_geral_gestor': ('.registro', 'ajuda_geral_gestor'),
    'ajuda_geral_solicitante': ('.registro', 'ajuda_geral_solicitante'),
    'ajuda_geral_tecnico': ('.registro', 'ajuda_geral_tecnico'),
    'classificar_emocao': ('.emocoes', 'classificar_emocao'),
    'compras': ('.compras', None),
    'criar_agente_ajuda_geral': ('.ajuda_geral', 'criar_agente_ajuda_geral'),
    'criar_agente_faq': ('.faq', 'criar_agente_faq'),
    'criar_agente_indicadores': ('.indicadores', 'criar_agente_indicadores'),
    'criar_agente_retorno_usuario': ('.retorno_usuario', 'criar_agente_retorno_usuario'),
    'criar_agente_solicitacoes': ('.solicitacoes', 'criar_agente_solicitacoes'),
    'criar_agente_visualizacao': ('.visualizacao', 'criar_agente_visualizacao'),
    'emocao_alternativa': ('.emocoes', 'emocao_alternativa'),
    'emocao_fluxo': ('.emocoes', 'emocao_fluxo'),
    'executar': ('.analista_compras', 'executar'),
    'faq_administrador': ('.registro', 'faq_administrador'),
    'faq_gestor': ('.registro', 'faq_gestor'),
    'faq_solicitante': ('.registro', 'faq_solicitante'),
    'faq_tecnico': ('.registro', 'faq_tecnico'),
    'feedback': ('.registro', 'feedback'),
    'formatar_contexto_conversa': ('.juiz', 'formatar_contexto_conversa'),
    'indicadores_administrador': ('.registro', 'indicadores_administrador'),
    'indicadores_gestor': ('.registro', 'indicadores_gestor'),
    'julgar_compra': ('.juiz_compras', 'julgar_compra'),
    'julgar_resposta': ('.juiz', 'julgar_resposta'),
    'llm_especialista': ('.modelos', 'llm_especialista'),
    'llm_luna': ('.modelos', 'llm_luna'),
    'llm_rapido': ('.modelos', 'llm_rapido'),
    'obter_modelo_embedding': ('.modelos', 'obter_modelo_embedding'),
    'obter_pergunta': ('.juiz', 'obter_pergunta'),
    'pedido_compra_explicito': ('.orquestrador', 'pedido_compra_explicito'),
    'prompts': ('.prompts', None),
    'resumir_operacoes': ('.emocoes', 'resumir_operacoes'),
    'revisar_resposta': ('.juiz', 'revisar_resposta'),
    'roteador_estruturado': ('.orquestrador', 'roteador_estruturado'),
    'rotear_orquestrador': ('.orquestrador', 'rotear_orquestrador'),
    'selecionar_agente': ('.registro', 'selecionar_agente'),
    'solicitacoes_administrador': ('.registro', 'solicitacoes_administrador'),
    'solicitacoes_gestor': ('.registro', 'solicitacoes_gestor'),
    'solicitacoes_solicitante': ('.registro', 'solicitacoes_solicitante'),
    'solicitacoes_tecnico': ('.registro', 'solicitacoes_tecnico'),
    'visualizacoes_administrador': ('.registro', 'visualizacoes_administrador'),
    'visualizacoes_gestor': ('.registro', 'visualizacoes_gestor'),
}

# Lista explícita para descoberta por IDEs, agentes e importações públicas.
__all__ = list(_EXPORTACOES)


def __getattr__(nome):
    """Resolve somente recursos da interface, preservando sua identidade original."""
    return _resolver_exportacao(nome, __name__, _EXPORTACOES, globals())


def __dir__():
    """Expõe os recursos disponíveis sem executar importações de domínios."""
    return sorted(set(globals()) | set(__all__))
