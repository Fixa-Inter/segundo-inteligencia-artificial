"""Regras e consultas disponíveis de visualização para os_conclusao."""

from types import MappingProxyType

from app.schemas.visualizacao import (
    Analise, ConsultaVisualizacaoPeriodo, ConsultaVisualizacaoSnapshot,
    FiltroObrigatorio, Fonte, ResultadoConsultaVisualizacao,
)
from .consultas import consultar_agregado


FONTE = Fonte(
    id="os_conclusao",
    tabela="workspace.fixa_pipeline.gold_dashboard_os_conclusao",
    chave=("ordem_servico_id",),
    campo_periodo="data_referencia",
    campo_snapshot=None,
)

FILTROS = MappingProxyType({
    "local_id": "BIGINT",
    "nome_local": "STRING",
    "tipo_local": "STRING",
    "tecnico_id": "BIGINT",
    "tecnico_nome": "STRING",
    "categoria_problema_id": "INT",
    "categoria_problema": "STRING",
    "status_id": "INT",
    "status_os": "STRING",
})

ANALISES: tuple[Analise, ...] = (
    Analise(
        "VIS-02", "OS finalizadas por período", FONTE, "serie_temporal",
        ("data_referencia",), "qtd_os_finalizadas", "SUM", "quantidade",
    ),
    Analise(
        "VIS-05", "Produtividade por técnico", FONTE, "categorias",
        ("tecnico_id", "tecnico_nome"), "qtd_os_finalizadas", "SUM", "quantidade",
    ),
    Analise(
        "VIS-07", "Distribuição do tempo de resolução", FONTE, "histograma",
        (), "tempo_resolucao_minutos", None, "minutos", excluir_nulos=True,
        excluir_negativos=True,
    ),
    Analise(
        "VIS-15", "Tempo de resolução por unidade", FONTE, "boxplot",
        ("unidade_id", "unidade_nome"), "tempo_resolucao_minutos", None, "minutos",
        excluir_nulos=True, excluir_negativos=True,
    ),
    Analise(
        "VIS-20", "Evolução do cumprimento dos prazos", FONTE, "serie_temporal",
        ("data_referencia",), "conclusao_prazo_pct_item", "AVG", "percentual",
        excluir_nulos=True, escala_percentual=100,
        filtros_obrigatorios=(FiltroObrigatorio("datas_prazo_validas", True),),
    ),
)


ANALISES_IMPLEMENTADAS = frozenset({"VIS-02", "VIS-05", "VIS-07", "VIS-15", "VIS-20"})


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
