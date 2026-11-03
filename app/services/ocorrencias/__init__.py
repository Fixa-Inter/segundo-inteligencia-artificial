"""Interface pública de app/services/ocorrencias; recursos carregados sob demanda."""

from app.core.interfaces import resolver_exportacao as _resolver_exportacao

# Cada nome aponta para seu proprietário; importar o pacote não inicializa clientes/agentes.
_EXPORTACOES = {
    'CAMPOS': ('.atualizarOcorrencia', 'CAMPOS'),
    'ENUMS': ('.atualizarOcorrencia', 'ENUMS'),
    'PERFIS': ('.atualizarOcorrencia', 'PERFIS'),
    'adicionar_ocorrencia': ('.criarOcorrencia', 'adicionar_ocorrencia'),
    'atualizar_propria_ativa': ('.atualizarOcorrencia', 'atualizar_propria_ativa'),
    'buscar_equipamento_por_codigo': ('.buscarOcorrencias', 'buscar_equipamento_por_codigo'),
    'buscar_proprias_ativas': ('.atualizarOcorrencia', 'buscar_proprias_ativas'),
    'consultar_minhas_ocorrencias': ('.buscarOcorrencias', 'consultar_minhas_ocorrencias'),
    'consultar_propria_ativa': ('.atualizarOcorrencia', 'consultar_propria_ativa'),
    'rotulos_enums': ('.atualizarOcorrencia', 'rotulos_enums'),
    'snapshot': ('.atualizarOcorrencia', 'snapshot'),
    'validar_alteracoes': ('.atualizarOcorrencia', 'validar_alteracoes'),
    'validar_usuario': ('.atualizarOcorrencia', 'validar_usuario'),
}

# Lista explícita para descoberta por IDEs, agentes e importações públicas.
__all__ = list(_EXPORTACOES)


def __getattr__(nome):
    """Resolve somente recursos da interface, preservando sua identidade original."""
    return _resolver_exportacao(nome, __name__, _EXPORTACOES, globals())


def __dir__():
    """Expõe os recursos disponíveis sem executar importações de domínios."""
    return sorted(set(globals()) | set(__all__))
