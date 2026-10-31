"""Regras e consultas disponíveis de visualização para recorrencia."""

from types import MappingProxyType

from app.schemas.visualizacao import (
    Analise, ConsultaVisualizacaoPeriodo, ConsultaVisualizacaoSnapshot,
    Fonte, ResultadoConsultaVisualizacao,
)
from .consultas import consultar_agregado


FONTE = Fonte(
    id="recorrencia",
    tabela="workspace.fixa_pipeline.gold_dashboard_recorrencia",
    chave=("unidade_id", "local_id", "categoria_equipamento_id", "data_referencia"),
    campo_periodo="data_referencia",
    campo_snapshot=None,
    ids_textuais=frozenset({"local_id", "categoria_equipamento_id"}),
)

FILTROS = MappingProxyType({
    "local_id": "STRING",
    "nome_local": "STRING",
    "tipo_local": "STRING",
    "categoria_equipamento_id": "STRING",
    "categoria_equipamento": "STRING",
})

ANALISES: tuple[Analise, ...] = (
    Analise(
        "VIS-12", "Episódios recorrentes por categoria", FONTE, "categorias",
        ("categoria_equipamento_id", "categoria_equipamento"),
        "qtd_episodios_recorrentes", "SUM", "quantidade",
    ),
    Analise(
        "VIS-13", "Recorrência por local", FONTE, "categorias",
        ("local_id", "nome_local"), "qtd_episodios_recorrentes", "SUM", "quantidade",
    ),
    Analise(
        "VIS-14", "Evolução da taxa de recorrência", FONTE, "serie_temporal",
        ("data_referencia",), "episodio_recorrente_pct_item", "AVG", "percentual",
        excluir_nulos=True, escala_percentual=100,
    ),
    Analise(
        "VIS-25", "Solicitações por episódio", FONTE, "histograma",
        (), "qtd_solicitacoes", None, "quantidade", excluir_nulos=True,
    ),
)


ANALISES_IMPLEMENTADAS = frozenset({"VIS-12", "VIS-13", "VIS-14", "VIS-25"})


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
