"""Interface pública de app/agents/prompts; recursos carregados sob demanda."""

from app.core.interfaces import resolver_exportacao as _resolver_exportacao

# Cada nome aponta para seu proprietário; importar o pacote não inicializa clientes/agentes.
_EXPORTACOES = {
    'construir_ajuda_geral_administrador': ('.construtor', 'construir_ajuda_geral_administrador'),
    'construir_ajuda_geral_gestor': ('.construtor', 'construir_ajuda_geral_gestor'),
    'construir_ajuda_geral_solicitante': ('.construtor', 'construir_ajuda_geral_solicitante'),
    'construir_ajuda_geral_tecnico': ('.construtor', 'construir_ajuda_geral_tecnico'),
    'construir_faq_administrador': ('.construtor', 'construir_faq_administrador'),
    'construir_faq_gestor': ('.construtor', 'construir_faq_gestor'),
    'construir_faq_solicitante': ('.construtor', 'construir_faq_solicitante'),
    'construir_faq_tecnico': ('.construtor', 'construir_faq_tecnico'),
    'construir_indicadores_administrador': ('.construtor', 'construir_indicadores_administrador'),
    'construir_indicadores_gestor': ('.construtor', 'construir_indicadores_gestor'),
    'construir_retorno_usuario': ('.construtor', 'construir_retorno_usuario'),
    'construir_solicitacoes_administrador': ('.construtor', 'construir_solicitacoes_administrador'),
    'construir_solicitacoes_gestor': ('.construtor', 'construir_solicitacoes_gestor'),
    'construir_solicitacoes_solicitante': ('.construtor', 'construir_solicitacoes_solicitante'),
    'construir_solicitacoes_tecnico': ('.construtor', 'construir_solicitacoes_tecnico'),
    'construir_visualizacoes_administrador': ('.construtor', 'construir_visualizacoes_administrador'),
    'construir_visualizacoes_gestor': ('.construtor', 'construir_visualizacoes_gestor'),
    'especialistas': ('.especialistas', None),
    'reutilizaveis': ('.reutilizaveis', None),
}

# Lista explícita para descoberta por IDEs, agentes e importações públicas.
__all__ = list(_EXPORTACOES)


def __getattr__(nome):
    """Resolve somente recursos da interface, preservando sua identidade original."""
    return _resolver_exportacao(nome, __name__, _EXPORTACOES, globals())


def __dir__():
    """Expõe os recursos disponíveis sem executar importações de domínios."""
    return sorted(set(globals()) | set(__all__))
