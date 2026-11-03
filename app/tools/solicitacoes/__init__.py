"""Interface pública de app/tools/solicitacoes; recursos carregados sob demanda."""

from app.core.interfaces import resolver_exportacao as _resolver_exportacao

# Cada nome aponta para seu proprietário; importar o pacote não inicializa clientes/agentes.
_EXPORTACOES = {
    'atualizar_solicitacao': ('.atualizarSolicitacao', 'atualizar_solicitacao'),
    'buscar_opcoes_solicitacao': ('.buscarOpcoes', 'buscar_opcoes_solicitacao'),
    'buscar_solicitacoes_para_atualizar': ('.atualizarSolicitacao', 'buscar_solicitacoes_para_atualizar'),
    'criar_solicitacao': ('.criarSolicitacao', 'criar_solicitacao'),
    'listar_minhas_solicitacoes': ('.listarMinhasSolicitacoes', 'listar_minhas_solicitacoes'),
    'listar_todas_solicitacoes_pendentes': ('.listarTodasSolicitacoesPendentes', 'listar_todas_solicitacoes_pendentes'),
    'processar_atualizacao': ('.atualizarSolicitacao', 'processar_atualizacao'),
    'processar_solicitacao': ('.criarSolicitacao', 'processar_solicitacao'),
    'salvar_rascunho_solicitacao': ('.criarSolicitacao', 'salvar_rascunho_solicitacao'),
}

# Lista explícita para descoberta por IDEs, agentes e importações públicas.
__all__ = list(_EXPORTACOES)


def __getattr__(nome):
    """Resolve somente recursos da interface, preservando sua identidade original."""
    return _resolver_exportacao(nome, __name__, _EXPORTACOES, globals())


def __dir__():
    """Expõe os recursos disponíveis sem executar importações de domínios."""
    return sorted(set(globals()) | set(__all__))
