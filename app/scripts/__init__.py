"""Interface pública de app/scripts; recursos carregados sob demanda."""

from app.core.interfaces import resolver_exportacao as _resolver_exportacao

# Cada nome aponta para seu proprietário; importar o pacote não inicializa clientes/agentes.
_EXPORTACOES = {
    'DIRETORIO_DOCUMENTOS_FAQ': ('.ingerir_faq', 'DIRETORIO_DOCUMENTOS_FAQ'),
    'PERFIS_FAQ': ('.ingerir_faq', 'PERFIS_FAQ'),
    'descobrir_documentos_faq': ('.ingerir_faq', 'descobrir_documentos_faq'),
    'main': ('.ingerir_faq', 'main'),
    'migrar_timestamps_mensagens': ('.migrar_timestamps_mensagens', 'migrar_timestamps_mensagens'),
}

# Lista explícita para descoberta por IDEs, agentes e importações públicas.
__all__ = list(_EXPORTACOES)


def __getattr__(nome):
    """Resolve somente recursos da interface, preservando sua identidade original."""
    return _resolver_exportacao(nome, __name__, _EXPORTACOES, globals())


def __dir__():
    """Expõe os recursos disponíveis sem executar importações de domínios."""
    return sorted(set(globals()) | set(__all__))
