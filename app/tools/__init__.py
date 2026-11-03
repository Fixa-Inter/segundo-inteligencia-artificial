"""Interface pública de app/tools; recursos carregados sob demanda."""

from app.core.interfaces import resolver_exportacao as _resolver_exportacao

# Cada nome aponta para seu proprietário; importar o pacote não inicializa clientes/agentes.
_EXPORTACOES = {
    'ArgumentosComRuntime': ('.argumentos', 'ArgumentosComRuntime'),
    'ajuda_geral': ('.ajuda_geral', None),
    'confirmou_selecao': ('.atualizacoes', 'confirmou_selecao'),
    'eventos': ('.eventos', None),
    'faq': ('.faq', None),
    'feedback': ('.feedback', None),
    'memoria': ('.memoria', None),
    'metricas_kpis': ('.metricas_kpis', None),
    'obter_contexto_cadastro': ('.contexto', 'obter_contexto_cadastro'),
    'ocorrencias': ('.ocorrencias', None),
    'ordensServico': ('.ordensServico', None),
    'resolver_rotulos': ('.propostas', 'resolver_rotulos'),
    'salvar_proposta': ('.atualizacoes', 'salvar_proposta'),
    'solicitacoes': ('.solicitacoes', None),
    'tecnicos': ('.tecnicos', None),
    'toolsRequest': ('.toolsRequest', None),
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
