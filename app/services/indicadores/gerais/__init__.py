"""Interface pública de app/services/indicadores/gerais; recursos carregados sob demanda."""

from app.core.interfaces import resolver_exportacao as _resolver_exportacao

# Cada nome aponta para seu proprietário; importar o pacote não inicializa clientes/agentes.
_EXPORTACOES = {
    'ConfiguracaoDatabricksAusente': ('.databricks', 'ConfiguracaoDatabricksAusente'),
    'ErroConsultaDatabricks': ('.databricks', 'ErroConsultaDatabricks'),
    'ErroDatabricks': ('.databricks', 'ErroDatabricks'),
    'ErroHTTPDatabricks': ('.databricks', 'ErroHTTPDatabricks'),
    'ResultadoDatabricksTruncado': ('.databricks', 'ResultadoDatabricksTruncado'),
    'TimeoutConsultaDatabricks': ('.databricks', 'TimeoutConsultaDatabricks'),
    'consultar_linhas_indicador': ('.consultas', 'consultar_linhas_indicador'),
    'executar_consulta': ('.databricks', 'executar_consulta'),
    'validar_periodo_indicadores': ('.consultas', 'validar_periodo_indicadores'),
    'validar_unidade_id': ('.unidade', 'validar_unidade_id'),
}

# Lista explícita para descoberta por IDEs, agentes e importações públicas.
__all__ = list(_EXPORTACOES)


def __getattr__(nome):
    """Resolve somente recursos da interface, preservando sua identidade original."""
    return _resolver_exportacao(nome, __name__, _EXPORTACOES, globals())


def __dir__():
    """Expõe os recursos disponíveis sem executar importações de domínios."""
    return sorted(set(globals()) | set(__all__))
