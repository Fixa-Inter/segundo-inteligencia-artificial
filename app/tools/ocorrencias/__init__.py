"""Interface pública de app/tools/ocorrencias; recursos carregados sob demanda."""

from app.core.interfaces import resolver_exportacao as _resolver_exportacao

# Cada nome aponta para seu proprietário; importar o pacote não inicializa clientes/agentes.
_EXPORTACOES = {
    'atualizar_ocorrencia': ('.atualizarOcorrencia', 'atualizar_ocorrencia'),
    'buscar_ocorrencias_para_atualizar': ('.atualizarOcorrencia', 'buscar_ocorrencias_para_atualizar'),
    'buscar_opcoes_ocorrencia': ('.buscarOpcoesOcorrencia', 'buscar_opcoes_ocorrencia'),
    'criar_ocorrencia': ('.criarOcorrencia', 'criar_ocorrencia'),
    'listar_minhas_ocorrencias': ('.listarMinhasOcorrencias', 'listar_minhas_ocorrencias'),
    'montar_tabela': ('.utilitarios', 'montar_tabela'),
    'processar_atualizacao': ('.atualizarOcorrencia', 'processar_atualizacao'),
    'processar_ocorrencia': ('.criarOcorrencia', 'processar_ocorrencia'),
    'salvar_rascunho_ocorrencia': ('.criarOcorrencia', 'salvar_rascunho_ocorrencia'),
}

# Lista explícita para descoberta por IDEs, agentes e importações públicas.
__all__ = list(_EXPORTACOES)


def __getattr__(nome):
    """Resolve somente recursos da interface, preservando sua identidade original."""
    return _resolver_exportacao(nome, __name__, _EXPORTACOES, globals())


def __dir__():
    """Expõe os recursos disponíveis sem executar importações de domínios."""
    return sorted(set(globals()) | set(__all__))
