"""Interface pública de app/agents/prompts/especialistas; recursos carregados sob demanda."""

from app.core.interfaces import resolver_exportacao as _resolver_exportacao

# Cada nome aponta para seu proprietário; importar o pacote não inicializa clientes/agentes.
_EXPORTACOES = {
    'AJUDA_GERAL_INSTRUCAO': ('.ajuda_geral', 'AJUDA_GERAL_INSTRUCAO'),
    'AJUDA_GERAL_INSTRUCAO_GESTOR': ('.ajuda_geral', 'AJUDA_GERAL_INSTRUCAO_GESTOR'),
    'AJUDA_GERAL_INSTRUCAO_SOLICITANTE_TECNICO': ('.ajuda_geral', 'AJUDA_GERAL_INSTRUCAO_SOLICITANTE_TECNICO'),
    'AJUDA_GERAL_INSTRUCAO_TECNICO_GESTOR': ('.ajuda_geral', 'AJUDA_GERAL_INSTRUCAO_TECNICO_GESTOR'),
    'CLASSIFICADOR_PROMPT_COMPLETO': ('.classificador', 'CLASSIFICADOR_PROMPT_COMPLETO'),
    'FAQ_INSTRUCAO': ('.faq', 'FAQ_INSTRUCAO'),
    'INDICADORES_INSTRUCAO': ('.indicadores', 'INDICADORES_INSTRUCAO'),
    'RETORNO_USUARIO_INSTRUCAO': ('.retorno_usuario', 'RETORNO_USUARIO_INSTRUCAO'),
    'SOLICITACOES_INSTRUCAO': ('.solicitacoes', 'SOLICITACOES_INSTRUCAO'),
    'VISUALIZACOES_INSTRUCAO': ('.visualizacoes', 'VISUALIZACOES_INSTRUCAO'),
}

# Lista explícita para descoberta por IDEs, agentes e importações públicas.
__all__ = list(_EXPORTACOES)


def __getattr__(nome):
    """Resolve somente recursos da interface, preservando sua identidade original."""
    return _resolver_exportacao(nome, __name__, _EXPORTACOES, globals())


def __dir__():
    """Expõe os recursos disponíveis sem executar importações de domínios."""
    return sorted(set(globals()) | set(__all__))
