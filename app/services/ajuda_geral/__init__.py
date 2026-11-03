"""Interface pública de app/services/ajuda_geral; recursos carregados sob demanda."""

from app.core.interfaces import resolver_exportacao as _resolver_exportacao

# Cada nome aponta para seu proprietário; importar o pacote não inicializa clientes/agentes.
_EXPORTACOES = {
    'CAMPOS_EDITAVEIS': ('.edicoes', 'CAMPOS_EDITAVEIS'),
    'CAMPOS_RELACIONAIS': ('.edicoes', 'CAMPOS_RELACIONAIS'),
    'COLECAO_GLOBAL': ('.consultas', 'COLECAO_GLOBAL'),
    'COLECOES_PERMITIDAS': ('.consultas', 'COLECOES_PERMITIDAS'),
    'COLECOES_SOLICITANTE': ('.consultas', 'COLECOES_SOLICITANTE'),
    'FKS_FOTO': ('.edicoes', 'FKS_FOTO'),
    'LIMITE_LISTAGEM': ('.consultas', 'LIMITE_LISTAGEM'),
    'LIMITE_LITERAL': ('.consultas', 'LIMITE_LITERAL'),
    'LIMITE_MULTIPLAS_COLECOES': ('.consultas', 'LIMITE_MULTIPLAS_COLECOES'),
    'LIMITE_POR_COLECAO': ('.consultas', 'LIMITE_POR_COLECAO'),
    'LIMITE_SEMANTICO': ('.consultas', 'LIMITE_SEMANTICO'),
    'LIMITE_SEMELHANTES': ('.consultas', 'LIMITE_SEMELHANTES'),
    'alterar_solicitacao': ('.edicoes', 'alterar_solicitacao'),
    'anexar_fotos': ('.edicoes', 'anexar_fotos'),
    'buscar_em_multiplas_colecoes': ('.consultas', 'buscar_em_multiplas_colecoes'),
    'buscar_problemas_por_local': ('.consultas_relacionais', 'buscar_problemas_por_local'),
    'buscar_semanticamente': ('.consultas', 'buscar_semanticamente'),
    'buscar_termo_literal': ('.consultas', 'buscar_termo_literal'),
    'buscar_textos_semelhantes': ('.consultas', 'buscar_textos_semelhantes'),
    'consultar_equipamento_por_codigo': ('.consultas_relacionais', 'consultar_equipamento_por_codigo'),
    'consultar_modelos_por_marca_categoria': ('.consultas_relacionais', 'consultar_modelos_por_marca_categoria'),
    'consultar_situacao_problema': ('.consultas_relacionais', 'consultar_situacao_problema'),
    'encontrar_codigo_equipamento': ('.consultas_relacionais', 'encontrar_codigo_equipamento'),
    'listar_equipamentos_por_local': ('.consultas_relacionais', 'listar_equipamentos_por_local'),
    'listar_eventos_por_local_e_periodo': ('.consultas_relacionais', 'listar_eventos_por_local_e_periodo'),
    'listar_observacoes_da_ordem': ('.consultas_relacionais', 'listar_observacoes_da_ordem'),
    'listar_ocorrencias_por_local': ('.consultas_relacionais', 'listar_ocorrencias_por_local'),
    'listar_registros': ('.consultas', 'listar_registros'),
    'listar_tarefas_da_ordem': ('.consultas_relacionais', 'listar_tarefas_da_ordem'),
    'localizar_opcao': ('.edicoes', 'localizar_opcao'),
    'localizar_registro': ('.edicoes', 'localizar_registro'),
}

# Lista explícita para descoberta por IDEs, agentes e importações públicas.
__all__ = list(_EXPORTACOES)


def __getattr__(nome):
    """Resolve somente recursos da interface, preservando sua identidade original."""
    return _resolver_exportacao(nome, __name__, _EXPORTACOES, globals())


def __dir__():
    """Expõe os recursos disponíveis sem executar importações de domínios."""
    return sorted(set(globals()) | set(__all__))
