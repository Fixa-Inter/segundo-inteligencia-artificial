"""Interface pública de app/services/sessoes; recursos carregados sob demanda."""

from app.core.interfaces import resolver_exportacao as _resolver_exportacao

# Cada nome aponta para seu proprietário; importar o pacote não inicializa clientes/agentes.
_EXPORTACOES = {
    'ErroConsultaHistorico': ('.historico', 'ErroConsultaHistorico'),
    'buscar_conversa': ('.historico', 'buscar_conversa'),
    'buscar_conversas_usuario': ('.historico', 'buscar_conversas_usuario'),
    'excluir_conversa': ('.historico', 'excluir_conversa'),
}

# Lista explícita para descoberta por IDEs, agentes e importações públicas.
__all__ = list(_EXPORTACOES)


def __getattr__(nome):
    """Resolve somente recursos da interface, preservando sua identidade original."""
    return _resolver_exportacao(nome, __name__, _EXPORTACOES, globals())


def __dir__():
    """Expõe os recursos disponíveis sem executar importações de domínios."""
    return sorted(set(globals()) | set(__all__))
