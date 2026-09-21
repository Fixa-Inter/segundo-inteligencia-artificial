from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies.permissions import exigir_perfis
from app.schemas.UsuarioContexto import UsuarioContexto
from app.schemas.analytics import (
    ComparacaoPeriodosRequest,
    PeriodoRequest,
)
from app.services.analytics.consultas import (
    comparar_periodos_mock,
    consultar_analytics_mock,
)


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


GestorAtual = Annotated[
    UsuarioContexto,
    Depends(exigir_perfis("gestor")),
]


@router.post("/resumo")
async def obter_resumo(
    periodo: PeriodoRequest,
    usuario: GestorAtual,
) -> dict:
    return consultar_analytics_mock(
        "resumo_periodo",
        periodo,
    )


@router.post("/tecnicos")
async def obter_metricas_tecnicos(
    periodo: PeriodoRequest,
    usuario: GestorAtual,
) -> dict:
    return consultar_analytics_mock(
        "metricas_tecnicos",
        periodo,
    )


@router.post("/categorias")
async def obter_chamados_por_categoria(
    periodo: PeriodoRequest,
    usuario: GestorAtual,
) -> dict:
    return consultar_analytics_mock(
        "chamados_por_categoria",
        periodo,
    )


@router.post("/locais")
async def obter_chamados_por_local(
    periodo: PeriodoRequest,
    usuario: GestorAtual,
) -> dict:
    return consultar_analytics_mock(
        "chamados_por_local",
        periodo,
    )


@router.post("/tempo-medio")
async def obter_tempo_medio_resolucao(
    periodo: PeriodoRequest,
    usuario: GestorAtual,
) -> dict:
    return consultar_analytics_mock(
        "tempo_medio_resolucao",
        periodo,
    )


@router.post("/atrasados")
async def obter_chamados_atrasados(
    periodo: PeriodoRequest,
    usuario: GestorAtual,
) -> dict:
    return consultar_analytics_mock(
        "chamados_atrasados",
        periodo,
    )


@router.post("/taxa-reabertura")
async def obter_taxa_reabertura(
    periodo: PeriodoRequest,
    usuario: GestorAtual,
) -> dict:
    return consultar_analytics_mock(
        "taxa_reabertura",
        periodo,
    )


@router.post("/comparacao")
async def comparar_periodos(
    dados: ComparacaoPeriodosRequest,
    usuario: GestorAtual,
) -> dict:
    return comparar_periodos_mock(dados)