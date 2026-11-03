"""Interface pública de app/tools/eventos; recursos carregados sob demanda."""

from app.core.interfaces import resolver_exportacao as _resolver_exportacao

# Cada nome aponta para seu proprietário; importar o pacote não inicializa clientes/agentes.
_EXPORTACOES = {
    'buscar_opcoes_evento': ('.buscarOpcoesEvento', 'buscar_opcoes_evento'),
    'criar_evento': ('.criarEvento', 'criar_evento'),
    'processar_evento': ('.criarEvento', 'processar_evento'),
    'salvar_rascunho_evento': ('.criarEvento', 'salvar_rascunho_evento'),
}

# Lista explícita para descoberta por IDEs, agentes e importações públicas.
__all__ = list(_EXPORTACOES)


def __getattr__(nome):
    """Resolve somente recursos da interface, preservando sua identidade original."""
    return _resolver_exportacao(nome, __name__, _EXPORTACOES, globals())


def __dir__():
    """Expõe os recursos disponíveis sem executar importações de domínios."""
    return sorted(set(globals()) | set(__all__))
