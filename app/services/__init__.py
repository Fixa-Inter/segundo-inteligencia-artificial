"""Interface pública de app/services; recursos carregados sob demanda."""

from app.core.interfaces import resolver_exportacao as _resolver_exportacao

# Cada nome aponta para seu proprietário; importar o pacote não inicializa clientes/agentes.
_EXPORTACOES = {
    'TIPOS': ('.operacoes', 'TIPOS'),
    'ajuda_geral': ('.ajuda_geral', None),
    'aprovacao_operacoes': ('.operacoes', 'aprovacao_operacoes'),
    'calcular_hash': ('.operacoes', 'calcular_hash'),
    'classificar_problema_dados': ('.classificacao_problema', 'classificar_problema_dados'),
    'eventos': ('.eventos', None),
    'feedback': ('.feedback', None),
    'finalizar_sessao_chat': ('.sessao', 'finalizar_sessao_chat'),
    'gerais': ('.gerais', None),
    'indicadores': ('.indicadores', None),
    'ocorrencias': ('.ocorrencias', None),
    'ordensServico': ('.ordensServico', None),
    'preparar_operacao': ('.operacoes', 'preparar_operacao'),
    'processar_chat': ('.chat', 'processar_chat'),
    'resumo': ('.operacoes', 'resumo'),
    'sessoes': ('.sessoes', None),
    'solicitacoes': ('.solicitacoes', None),
    'tecnicos': ('.tecnicos', None),
    'visualizacoes': ('.visualizacoes', None),
}

# Lista explícita para descoberta por IDEs, agentes e importações públicas.
__all__ = list(_EXPORTACOES)


def __getattr__(nome):
    """Resolve somente recursos da interface, preservando sua identidade original."""
    return _resolver_exportacao(nome, __name__, _EXPORTACOES, globals())


def __dir__():
    """Expõe os recursos disponíveis sem executar importações de domínios."""
    return sorted(set(globals()) | set(__all__))
