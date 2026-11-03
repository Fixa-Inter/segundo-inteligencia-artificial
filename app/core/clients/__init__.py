"""Interface pública de app/core/clients; recursos carregados sob demanda."""

from app.core.interfaces import resolver_exportacao as _resolver_exportacao

# Cada nome aponta para seu proprietário; importar o pacote não inicializa clientes/agentes.
_EXPORTACOES = {
    'abrir_cliente_mongo': ('.mongo', 'abrir_cliente_mongo'),
    'abrir_cliente_qdrant': ('.qdrant', 'abrir_cliente_qdrant'),
    'executar_consulta': ('.postgres', 'executar_consulta'),
    'executar_insercao': ('.postgres', 'executar_insercao'),
    'fechar_cliente_databricks': ('.databricks', 'fechar_cliente_databricks'),
    'fechar_cliente_mongo': ('.mongo', 'fechar_cliente_mongo'),
    'fechar_cliente_qdrant': ('.qdrant', 'fechar_cliente_qdrant'),
    'fechar_conexoes_postgres': ('.postgres', 'fechar_conexoes_postgres'),
    'iniciar_cliente_mongo': ('.mongo', 'iniciar_cliente_mongo'),
    'iniciar_cliente_qdrant': ('.qdrant', 'iniciar_cliente_qdrant'),
    'llm_especialista': ('.modelos', 'llm_especialista'),
    'llm_luna': ('.modelos', 'llm_luna'),
    'llm_rapido': ('.modelos', 'llm_rapido'),
    'obter_cliente_databricks': ('.databricks', 'obter_cliente_databricks'),
    'obter_modelo_embedding': ('.modelos', 'obter_modelo_embedding'),
    'obter_motor': ('.postgres', 'obter_motor'),
    'validar_config_mongo': ('.mongo', 'validar_config_mongo'),
}

# Lista explícita para descoberta por IDEs, agentes e importações públicas.
__all__ = list(_EXPORTACOES)


def __getattr__(nome):
    """Resolve somente recursos da interface, preservando sua identidade original."""
    return _resolver_exportacao(nome, __name__, _EXPORTACOES, globals())


def __dir__():
    """Expõe os recursos disponíveis sem executar importações de domínios."""
    return sorted(set(globals()) | set(__all__))
