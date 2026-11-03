"""Interface pública de app/api/routes; recursos carregados sob demanda."""

from app.core.interfaces import resolver_exportacao as _resolver_exportacao

# Cada nome aponta para seu proprietário; importar o pacote não inicializa clientes/agentes.
_EXPORTACOES = {
    'classificar_problema': ('.classificacao_problema', 'classificar_problema'),
    'conversar': ('.chat', 'conversar'),
    'encerrar_conversa': ('.chat', 'encerrar_conversa'),
    'excluir_conversa_historico': ('.sessoes', 'excluir_conversa_historico'),
    'health_check': ('.health', 'health_check'),
    'metrics': ('.metrics', 'metrics'),
    'pegar_conversa_especifica': ('.sessoes', 'pegar_conversa_especifica'),
    'pegar_todas_conversas_usuario': ('.sessoes', 'pegar_todas_conversas_usuario'),
    'router_CHAT': ('.chat', 'router'),
    'router_CLASSIFICACAO_PROBLEMA': ('.classificacao_problema', 'router'),
    'router_HEALTH': ('.health', 'router'),
    'router_METRICS': ('.metrics', 'router'),
    'router_SESSOES': ('.sessoes', 'router'),
}

# Lista explícita para descoberta por IDEs, agentes e importações públicas.
__all__ = list(_EXPORTACOES)


def __getattr__(nome):
    """Resolve somente recursos da interface, preservando sua identidade original."""
    return _resolver_exportacao(nome, __name__, _EXPORTACOES, globals())


def __dir__():
    """Expõe os recursos disponíveis sem executar importações de domínios."""
    return sorted(set(globals()) | set(__all__))
