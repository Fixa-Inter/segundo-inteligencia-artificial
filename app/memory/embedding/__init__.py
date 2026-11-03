"""Interface pública de app/memory/embedding; recursos carregados sob demanda."""

from app.core.interfaces import resolver_exportacao as _resolver_exportacao

# Cada nome aponta para seu proprietário; importar o pacote não inicializa clientes/agentes.
_EXPORTACOES = {
    'SOBREPOSICAO_TRECHOS': ('.popular_banco_vetorial', 'SOBREPOSICAO_TRECHOS'),
    'TAMANHO_LOTE': ('.popular_banco_vetorial', 'TAMANHO_LOTE'),
    'TAMANHO_TRECHO': ('.popular_banco_vetorial', 'TAMANHO_TRECHO'),
    'carregar_documentos_faq': ('.popular_banco_vetorial', 'carregar_documentos_faq'),
    'gerar_ponto_id': ('.configuracao', 'gerar_ponto_id'),
    'gerar_vetor_documento': ('.configuracao', 'gerar_vetor_documento'),
    'gerar_vetor_operacional': ('.configuracao', 'gerar_vetor_operacional'),
    'gerar_vetores_documentos': ('.configuracao', 'gerar_vetores_documentos'),
    'ingerir_faq': ('.popular_banco_vetorial', 'ingerir_faq'),
    'obter_vetorizador': ('.configuracao', 'obter_vetorizador'),
    'obter_vetorizador_operacional': ('.configuracao', 'obter_vetorizador_operacional'),
}

# Lista explícita para descoberta por IDEs, agentes e importações públicas.
__all__ = list(_EXPORTACOES)


def __getattr__(nome):
    """Resolve somente recursos da interface, preservando sua identidade original."""
    return _resolver_exportacao(nome, __name__, _EXPORTACOES, globals())


def __dir__():
    """Expõe os recursos disponíveis sem executar importações de domínios."""
    return sorted(set(globals()) | set(__all__))
