"""Interface pública de app/mcp/pechincha; recursos carregados sob demanda."""

from app.core.interfaces import resolver_exportacao as _resolver_exportacao

# Cada nome aponta para seu proprietário; importar o pacote não inicializa clientes/agentes.
_EXPORTACOES = {
    'BuscaOfertas': ('.modelos', 'BuscaOfertas'),
    'ErroPechincha': ('.transporte', 'ErroPechincha'),
    'buscar_ofertas': ('.ferramentas', 'buscar_ofertas'),
    'chamar_ferramenta': ('.transporte', 'chamar_ferramenta'),
    'listar_categorias': ('.ferramentas', 'listar_categorias'),
    'listar_lojas': ('.ferramentas', 'listar_lojas'),
    'normalizar_ofertas': ('.modelos', 'normalizar_ofertas'),
}

# Lista explícita para descoberta por IDEs, agentes e importações públicas.
__all__ = list(_EXPORTACOES)


def __getattr__(nome):
    """Resolve somente recursos da interface, preservando sua identidade original."""
    return _resolver_exportacao(nome, __name__, _EXPORTACOES, globals())


def __dir__():
    """Expõe os recursos disponíveis sem executar importações de domínios."""
    return sorted(set(globals()) | set(__all__))
