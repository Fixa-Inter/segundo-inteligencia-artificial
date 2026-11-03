"""Interface pública de app/services/solicitacoes; recursos carregados sob demanda."""

from app.core.interfaces import resolver_exportacao as _resolver_exportacao

# Cada nome aponta para seu proprietário; importar o pacote não inicializa clientes/agentes.
_EXPORTACOES = {
    'CAMPOS': ('.atualizarSolicitacao', 'CAMPOS'),
    'adicionar_solicitacao': ('.criarSolicitacao', 'adicionar_solicitacao'),
    'atualizar_propria_pendente': ('.atualizarSolicitacao', 'atualizar_propria_pendente'),
    'buscar_proprias_pendentes': ('.atualizarSolicitacao', 'buscar_proprias_pendentes'),
    'consultar_propria_pendente': ('.atualizarSolicitacao', 'consultar_propria_pendente'),
    'listar_minhas_solicitacoes': ('.buscarSolicitacao', 'listar_minhas_solicitacoes'),
    'listar_solicitacoes_pendentes': ('.buscarSolicitacao', 'listar_solicitacoes_pendentes'),
    'snapshot': ('.atualizarSolicitacao', 'snapshot'),
    'validar_alteracoes': ('.atualizarSolicitacao', 'validar_alteracoes'),
}

# Lista explícita para descoberta por IDEs, agentes e importações públicas.
__all__ = list(_EXPORTACOES)


def __getattr__(nome):
    """Resolve somente recursos da interface, preservando sua identidade original."""
    return _resolver_exportacao(nome, __name__, _EXPORTACOES, globals())


def __dir__():
    """Expõe os recursos disponíveis sem executar importações de domínios."""
    return sorted(set(globals()) | set(__all__))
