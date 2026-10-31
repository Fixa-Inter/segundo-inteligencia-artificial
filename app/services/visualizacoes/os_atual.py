"""Regras e consultas disponíveis de visualização para os_atual."""

from types import MappingProxyType

from app.schemas.visualizacao import (
    Analise, ConsultaVisualizacaoPeriodo, ConsultaVisualizacaoSnapshot,
    FiltroObrigatorio, Fonte, ResultadoConsultaVisualizacao,
)
from .consultas import consultar_agregado


FONTE = Fonte(
    id="os_atual",
    tabela="workspace.fixa_pipeline.gold_dashboard_os_atual",
    chave=("ordem_servico_id",),
    campo_periodo=None,
    campo_snapshot="data_referencia_snapshot",
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
    "os_aberta": "INT",
    "os_atrasada": "INT",
    "os_prazo_vencido": "INT",
})

ANALISES: tuple[Analise, ...] = (
    Analise(
        "VIS-03", "Distribuição das OS por status", FONTE, "categorias",
        ("status_id", "status_os"), "ordem_servico_id", "COUNT", "quantidade",
    ),
    Analise(
        "VIS-04", "Carga ativa por técnico", FONTE, "categorias",
        ("tecnico_id", "tecnico_nome"), "os_aberta", "SUM", "quantidade",
        filtros_obrigatorios=(FiltroObrigatorio("os_aberta", 1),),
    ),
    Analise(
        "VIS-22", "OS abertas com prazo vencido por local", FONTE, "categorias",
        ("local_id", "nome_local"), "os_prazo_vencido", "SUM", "quantidade",
        filtros_obrigatorios=(FiltroObrigatorio("os_aberta", 1),),
    ),
)


ANALISES_IMPLEMENTADAS = frozenset({"VIS-03", "VIS-04", "VIS-22"})


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
