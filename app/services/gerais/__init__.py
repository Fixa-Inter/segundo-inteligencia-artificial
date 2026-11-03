"""Interface pública de app/services/gerais; recursos carregados sob demanda."""

from app.core.interfaces import resolver_exportacao as _resolver_exportacao

# Cada nome aponta para seu proprietário; importar o pacote não inicializa clientes/agentes.
_EXPORTACOES = {
    'CRITERIOS_INTENCAO': ('.rotear', 'CRITERIOS_INTENCAO'),
    'DecisaoIncertaJEV': ('.jev', 'DecisaoIncertaJEV'),
    'ErroConsultaPerfil': ('.perfil', 'ErroConsultaPerfil'),
    'ErroJEV': ('.jev', 'ErroJEV'),
    'INSTRUCAO_INTENCAO': ('.rotear', 'INSTRUCAO_INTENCAO'),
    'consultar_jev': ('.jev', 'consultar_jev'),
    'consultar_perfil': ('.perfil', 'consultar_perfil'),
    'interpretar_cadastro': ('.cadastros', 'interpretar_cadastro'),
    'julgar_jev': ('.julgar', 'julgar_jev'),
    'ler_choice': ('.jev', 'ler_choice'),
    'ler_noul': ('.jev', 'ler_noul'),
    'obter_unidade_id': ('.unidade', 'obter_unidade_id'),
    'rotear_jev': ('.rotear', 'rotear_jev'),
}

# Lista explícita para descoberta por IDEs, agentes e importações públicas.
__all__ = list(_EXPORTACOES)


def __getattr__(nome):
    """Resolve somente recursos da interface, preservando sua identidade original."""
    return _resolver_exportacao(nome, __name__, _EXPORTACOES, globals())


def __dir__():
    """Expõe os recursos disponíveis sem executar importações de domínios."""
    return sorted(set(globals()) | set(__all__))
