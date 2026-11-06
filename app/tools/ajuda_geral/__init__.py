"""Interface pública de app/tools/ajuda_geral; recursos carregados sob demanda."""

from app.core.interfaces import resolver_exportacao as _resolver_exportacao

# Cada nome aponta para seu proprietário; importar o pacote não inicializa clientes/agentes.
_EXPORTACOES = {
    'contar_meus_registros': ('.contagens', 'contar_meus_registros'),
    'Colecao': ('.consultas', 'Colecao'),
    'ColecaoSolicitante': ('.consultas', 'ColecaoSolicitante'),
    'Tipo': ('.edicoes', 'Tipo'),
    'alterar_informacao_solicitacao': ('.edicoes', 'alterar_informacao_solicitacao'),
    'anexar_foto_observacao_conclusao': ('.edicoes', 'anexar_foto_observacao_conclusao'),
    'anexar_foto_ocorrencia': ('.edicoes', 'anexar_foto_ocorrencia'),
    'anexar_foto_solicitacao': ('.edicoes', 'anexar_foto_solicitacao'),
    'buscar_em_multiplas_colecoes': ('.consultas', 'buscar_em_multiplas_colecoes'),
    'buscar_em_multiplas_colecoes_solicitante': ('.consultas', 'buscar_em_multiplas_colecoes_solicitante'),
    'buscar_problemas_por_local': ('.consultas_relacionais', 'buscar_problemas_por_local'),
    'buscar_semanticamente': ('.consultas', 'buscar_semanticamente'),
    'buscar_semanticamente_solicitante': ('.consultas', 'buscar_semanticamente_solicitante'),
    'buscar_termo_literal': ('.consultas', 'buscar_termo_literal'),
    'buscar_termo_literal_solicitante': ('.consultas', 'buscar_termo_literal_solicitante'),
    'buscar_textos_semelhantes': ('.consultas', 'buscar_textos_semelhantes'),
    'buscar_textos_semelhantes_solicitante': ('.consultas', 'buscar_textos_semelhantes_solicitante'),
    'consultar_equipamento_por_codigo': ('.consultas_relacionais', 'consultar_equipamento_por_codigo'),
    'consultar_modelos_por_marca_categoria': ('.consultas_relacionais', 'consultar_modelos_por_marca_categoria'),
    'consultar_situacao_problema': ('.consultas_relacionais', 'consultar_situacao_problema'),
    'encontrar_codigo_equipamento': ('.consultas_relacionais', 'encontrar_codigo_equipamento'),
    'listar_equipamentos_por_local': ('.consultas_relacionais', 'listar_equipamentos_por_local'),
    'listar_eventos_por_local_e_periodo': ('.consultas_relacionais', 'listar_eventos_por_local_e_periodo'),
    'listar_observacoes_da_ordem': ('.consultas_relacionais', 'listar_observacoes_da_ordem'),
    'listar_ocorrencias_por_local': ('.consultas_relacionais', 'listar_ocorrencias_por_local'),
    'listar_registros': ('.consultas', 'listar_registros'),
    'listar_registros_solicitante': ('.consultas', 'listar_registros_solicitante'),
    'listar_tarefas_da_ordem': ('.consultas_relacionais', 'listar_tarefas_da_ordem'),
}

# Lista explícita para descoberta por IDEs, agentes e importações públicas.
__all__ = list(_EXPORTACOES)


def __getattr__(nome):
    """Resolve somente recursos da interface, preservando sua identidade original."""
    return _resolver_exportacao(nome, __name__, _EXPORTACOES, globals())


def __dir__():
    """Expõe os recursos disponíveis sem executar importações de domínios."""
    return sorted(set(globals()) | set(__all__))
