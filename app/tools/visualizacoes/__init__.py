"""Interface pública de app/tools/visualizacoes; recursos carregados sob demanda."""

from app.core.interfaces import resolver_exportacao as _resolver_exportacao

# Cada nome aponta para seu proprietário; importar o pacote não inicializa clientes/agentes.
_EXPORTACOES = {
    'FERRAMENTAS_VISUALIZACOES': ('.registro', 'FERRAMENTAS_VISUALIZACOES'),
    'FILTROS_POR_FONTE': ('.filtros', 'FILTROS_POR_FONTE'),
    'consultar_visualizacao_ocorrencia': ('.consultas', 'consultar_visualizacao_ocorrencia'),
    'consultar_visualizacao_os_atual': ('.consultas', 'consultar_visualizacao_os_atual'),
    'consultar_visualizacao_os_conclusao': ('.consultas', 'consultar_visualizacao_os_conclusao'),
    'consultar_visualizacao_os_criacao': ('.consultas', 'consultar_visualizacao_os_criacao'),
    'consultar_visualizacao_recorrencia': ('.consultas', 'consultar_visualizacao_recorrencia'),
    'consultar_visualizacao_solicitacao': ('.consultas', 'consultar_visualizacao_solicitacao'),
    'criar_tool': ('.execucao', 'criar_tool'),
    'resolver_unidade': ('.contexto', 'resolver_unidade'),
    'validar_acesso': ('.contexto', 'validar_acesso'),
    'validar_campos_filtro': ('.filtros', 'validar_campos_filtro'),
    'validar_consulta': ('.filtros', 'validar_consulta'),
}

# Lista explícita para descoberta por IDEs, agentes e importações públicas.
__all__ = list(_EXPORTACOES)


def __getattr__(nome):
    """Resolve somente recursos da interface, preservando sua identidade original."""
    return _resolver_exportacao(nome, __name__, _EXPORTACOES, globals())


def __dir__():
    """Expõe os recursos disponíveis sem executar importações de domínios."""
    return sorted(set(globals()) | set(__all__))
