"""Regras e consultas disponíveis de visualização para ocorrencia."""

from types import MappingProxyType

from app.schemas.visualizacao import (
    Analise, ConsultaVisualizacaoPeriodo, ConsultaVisualizacaoSnapshot,
    Fonte, ResultadoConsultaVisualizacao,
)
from .consultas import consultar_agregado


FONTE = Fonte(
    id="ocorrencia",
    tabela="workspace.fixa_pipeline.gold_dashboard_ocorrencia",
    chave=("ocorrencia_id",),
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
    "categoria_equipamento_id": "BIGINT",
    "categoria_equipamento": "STRING",
    "prioridade": "INT",
    "prioridade_nome": "STRING",
    "esta_ativo": "BOOLEAN",
})

ANALISES: tuple[Analise, ...] = (
    Analise(
        "VIS-26", "Ocorrências por período e prioridade", FONTE, "serie_temporal",
        ("data_referencia", "prioridade", "prioridade_nome"),
        "qtd_ocorrencias", "SUM", "quantidade",
    ),
    Analise(
        "VIS-27", "Ocorrências de alta prioridade por local", FONTE, "categorias",
        ("local_id", "nome_local"), "ocorrencia_alta_prioridade", "SUM", "quantidade",
    ),
)


ANALISES_IMPLEMENTADAS = frozenset({"VIS-26", "VIS-27"})


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
