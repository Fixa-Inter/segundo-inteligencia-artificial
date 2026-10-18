"""Interface pública do domínio."""

from .consultas import (
    buscar_semanticamente,
    buscar_em_multiplas_colecoes,
    listar_registros,
    buscar_termo_literal,
    buscar_textos_semelhantes,
    buscar_semanticamente_solicitante,
    buscar_em_multiplas_colecoes_solicitante,
    listar_registros_solicitante,
    buscar_termo_literal_solicitante,
    buscar_textos_semelhantes_solicitante,
)
from .consultas_relacionais import (
    buscar_problemas_por_local,
    consultar_situacao_problema,
    consultar_modelos_por_marca_categoria,
    consultar_equipamento_por_codigo,
    encontrar_codigo_equipamento,
    listar_equipamentos_por_local,
    listar_ocorrencias_por_local,
    listar_tarefas_da_ordem,
    listar_observacoes_da_ordem,
    listar_eventos_por_local_e_periodo,
)
from .edicoes import (
    alterar_informacao_solicitacao,
    anexar_foto_solicitacao,
    anexar_foto_ocorrencia,
    anexar_foto_observacao_conclusao,
)

__all__ = [
    "buscar_semanticamente",
    "buscar_em_multiplas_colecoes",
    "listar_registros",
    "buscar_termo_literal",
    "buscar_textos_semelhantes",
    "buscar_semanticamente_solicitante",
    "buscar_em_multiplas_colecoes_solicitante",
    "listar_registros_solicitante",
    "buscar_termo_literal_solicitante",
    "buscar_textos_semelhantes_solicitante",
    "buscar_problemas_por_local",
    "consultar_situacao_problema",
    "consultar_modelos_por_marca_categoria",
    "consultar_equipamento_por_codigo",
    "encontrar_codigo_equipamento",
    "listar_equipamentos_por_local",
    "listar_ocorrencias_por_local",
    "listar_tarefas_da_ordem",
    "listar_observacoes_da_ordem",
    "listar_eventos_por_local_e_periodo",
    "alterar_informacao_solicitacao",
    "anexar_foto_solicitacao",
    "anexar_foto_ocorrencia",
    "anexar_foto_observacao_conclusao",
]
