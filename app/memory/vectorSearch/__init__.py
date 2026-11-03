"""Interface pública de app/memory/vectorSearch; recursos carregados sob demanda."""

from app.core.interfaces import resolver_exportacao as _resolver_exportacao

# Cada nome aponta para seu proprietário; importar o pacote não inicializa clientes/agentes.
_EXPORTACOES = {
    'buscar_categoria_equipamento': ('.busca', 'buscar_categoria_equipamento'),
    'buscar_local_endereco': ('.busca', 'buscar_local_endereco'),
    'garantir_indice_faq': ('.garantir_indice', 'garantir_indice_faq'),
    'garantir_indice_historico': ('.garantir_indice', 'garantir_indice_historico'),
    'garantir_indices_operacionais': ('.garantir_indice', 'garantir_indices_operacionais'),
    'recuperar_historico': ('.recuperar_historico', 'recuperar_historico'),
    'validar_selecao': ('.busca', 'validar_selecao'),
}

# Lista explícita para descoberta por IDEs, agentes e importações públicas.
__all__ = list(_EXPORTACOES)


def __getattr__(nome):
    """Resolve somente recursos da interface, preservando sua identidade original."""
    return _resolver_exportacao(nome, __name__, _EXPORTACOES, globals())


def __dir__():
    """Expõe os recursos disponíveis sem executar importações de domínios."""
    return sorted(set(globals()) | set(__all__))
