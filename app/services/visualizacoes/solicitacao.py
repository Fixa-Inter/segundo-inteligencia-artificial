"""Regras e consultas disponíveis de visualização para solicitacao."""

from types import MappingProxyType

from app.schemas.visualizacao import (
    Analise, ConsultaVisualizacaoPeriodo, ConsultaVisualizacaoSnapshot,
    Fonte, ResultadoConsultaVisualizacao,
)
from .consultas import consultar_agregado


FONTE = Fonte(
    id="solicitacao",
    tabela="workspace.fixa_pipeline.gold_dashboard_solicitacao",
    chave=("problema_id",),
    campo_periodo="data_referencia",
    campo_snapshot=None,
)

FILTROS = MappingProxyType({
    "local_id": "BIGINT",
    "nome_local": "STRING",
    "tipo_local": "STRING",
    "categoria_equipamento_id": "BIGINT",
    "categoria_equipamento": "STRING",
    "status_problema_id": "INT",
    "status_problema": "STRING",
})

ANALISES: tuple[Analise, ...] = (
    Analise(
        "VIS-08", "Solicitações por status", FONTE, "categorias",
        ("status_problema_id", "status_problema"), "qtd_solicitacoes", "SUM", "quantidade",
    ),
    Analise(
        "VIS-09", "Solicitações criadas por período", FONTE, "serie_temporal",
        ("data_referencia",), "qtd_solicitacoes", "SUM", "quantidade",
    ),
    Analise(
        "VIS-10", "Solicitações por local", FONTE, "categorias",
        ("local_id", "nome_local"), "qtd_solicitacoes", "SUM", "quantidade",
    ),
    Analise(
        "VIS-11", "Solicitações por categoria de equipamento", FONTE, "categorias",
        ("categoria_equipamento_id", "categoria_equipamento"),
        "qtd_solicitacoes", "SUM", "quantidade",
    ),
    Analise(
        "VIS-23", "Conversão de solicitações em OS por categoria", FONTE, "categorias",
        ("categoria_equipamento_id", "categoria_equipamento"),
        "conversao_os_pct_item", "AVG", "percentual", excluir_nulos=True, escala_percentual=100,
    ),
    Analise(
        "VIS-24", "Reprovação de solicitações por local", FONTE, "categorias",
        ("local_id", "nome_local"), "reprovacao_pct_item", "AVG", "percentual",
        excluir_nulos=True, escala_percentual=100,
    ),
)


ANALISES_IMPLEMENTADAS = frozenset({"VIS-08", "VIS-09", "VIS-10", "VIS-11", "VIS-23", "VIS-24"})


async def consultar(
    consulta: ConsultaVisualizacaoPeriodo | ConsultaVisualizacaoSnapshot,
    *,
    unidade_id: int,
) -> ResultadoConsultaVisualizacao:
    """Consulta apenas análises implementadas desta fonte e da unidade recebida do servidor."""
    return await consultar_agregado(
        consulta, unidade_id=unidade_id, analises=ANALISES,
        filtros_permitidos=FILTROS, implementadas=ANALISES_IMPLEMENTADAS,
    )
