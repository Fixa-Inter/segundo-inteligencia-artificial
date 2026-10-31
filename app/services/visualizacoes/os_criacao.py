"""Regras e consultas disponíveis de visualização para os_criacao."""

from types import MappingProxyType

from app.schemas.visualizacao import (
    Analise, ConsultaVisualizacaoPeriodo, ConsultaVisualizacaoSnapshot,
    Fonte, ResultadoConsultaVisualizacao,
)
from .consultas import consultar_agregado


FONTE = Fonte(
    id="os_criacao",
    tabela="workspace.fixa_pipeline.gold_dashboard_os_criacao",
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
        "VIS-01", "OS criadas por período", FONTE, "serie_temporal",
        ("data_referencia",), "qtd_os", "SUM", "quantidade",
    ),
    Analise(
        "VIS-06", "Distribuição do tempo de espera", FONTE, "histograma",
        (), "tempo_espera_minutos", None, "minutos", excluir_nulos=True,
        excluir_negativos=True,
    ),
    Analise(
        "VIS-16", "Tempo pausado por categoria de problema", FONTE, "boxplot",
        ("categoria_problema_id", "categoria_problema"),
        "tempo_pausado_minutos", None, "minutos", excluir_nulos=True,
        excluir_negativos=True,
    ),
    Analise(
        "VIS-17", "Tempo de espera por tipo de local", FONTE, "boxplot",
        ("tipo_local",), "tempo_espera_minutos", None, "minutos", excluir_nulos=True,
        excluir_negativos=True,
    ),
    Analise(
        "VIS-18", "Reabertura por categoria de problema", FONTE, "categorias",
        ("categoria_problema_id", "categoria_problema"),
        "reabertura_pct_item", "AVG", "percentual", excluir_nulos=True, escala_percentual=100,
    ),
    Analise(
        "VIS-19", "Reatribuição por técnico", FONTE, "categorias",
        ("tecnico_id", "tecnico_nome"), "reatribuicao_pct_item", "AVG", "percentual",
        excluir_nulos=True, escala_percentual=100,
    ),
    Analise(
        "VIS-21", "Tempo médio de pausa por categoria de problema", FONTE, "categorias",
        ("categoria_problema_id", "categoria_problema"),
        "tempo_pausado_minutos", "AVG", "minutos", excluir_nulos=True,
        excluir_negativos=True,
    ),
)


ANALISES_IMPLEMENTADAS = frozenset({"VIS-01", "VIS-06", "VIS-16", "VIS-17", "VIS-18", "VIS-19", "VIS-21"})


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
