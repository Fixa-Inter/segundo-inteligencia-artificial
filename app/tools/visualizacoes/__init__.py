"""Tools analíticas de visualização e validação dos seus argumentos."""

from .filtros import validar_campos_filtro, validar_consulta
from .consultas import (
    consultar_visualizacao_os_criacao, consultar_visualizacao_os_conclusao,
    consultar_visualizacao_os_atual, consultar_visualizacao_solicitacao,
    consultar_visualizacao_recorrencia, consultar_visualizacao_ocorrencia,
)

FERRAMENTAS_VISUALIZACOES = (
    consultar_visualizacao_os_criacao, consultar_visualizacao_os_conclusao,
    consultar_visualizacao_os_atual, consultar_visualizacao_solicitacao,
    consultar_visualizacao_recorrencia, consultar_visualizacao_ocorrencia,
)

__all__ = [
    "validar_campos_filtro", "validar_consulta", "FERRAMENTAS_VISUALIZACOES",
    *(ferramenta.name for ferramenta in FERRAMENTAS_VISUALIZACOES),
]
