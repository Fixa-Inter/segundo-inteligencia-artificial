"""Tools gerenciais para métricas de ocorrências."""

from datetime import date
from typing import Literal

from langchain.tools import ToolRuntime, tool
from pydantic import Field

from app.services.indicadores import ocorrencia as servico
from app.tools.metricas_kpis.ordem_servico import (
    _ArgumentosPeriodo,
    _validar_gestor,
)


class _ArgumentosPeriodoGranularidade(_ArgumentosPeriodo):
    granularidade: Literal["dia", "mes", "ano"] = Field(
        description="Agrupamento temporal: dia, mes ou ano.",
    )


@tool(args_schema=_ArgumentosPeriodo)
async def obter_total_ocorrencias(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Conta ocorrências criadas no período [início, fim)."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_total_ocorrencias(inicio, fim)


@tool(args_schema=_ArgumentosPeriodo)
async def obter_ocorrencias_por_tecnico(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Lista o volume de ocorrências criadas por técnico no período."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_ocorrencias_por_tecnico(inicio, fim)


@tool(args_schema=_ArgumentosPeriodo)
async def obter_ocorrencias_por_unidade(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Lista o volume de ocorrências criadas por unidade no período."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_ocorrencias_por_unidade(inicio, fim)


@tool(args_schema=_ArgumentosPeriodo)
async def obter_ocorrencias_por_local(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Lista o volume de ocorrências criadas por local no período."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_ocorrencias_por_local(inicio, fim)


@tool(args_schema=_ArgumentosPeriodo)
async def obter_ocorrencias_por_categoria_problema(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Lista ocorrências por categoria de problema no período."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_ocorrencias_por_categoria_problema(inicio, fim)


@tool(args_schema=_ArgumentosPeriodo)
async def obter_ocorrencias_por_categoria_equipamento(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Lista ocorrências agrupadas por categoria de equipamento."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_ocorrencias_por_categoria_equipamento(inicio, fim)


@tool(args_schema=_ArgumentosPeriodo)
async def obter_ocorrencias_por_prioridade(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Lista ocorrências por prioridade: alta 0, média 1, baixa 2."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_ocorrencias_por_prioridade(inicio, fim)


@tool(args_schema=_ArgumentosPeriodo)
async def obter_ocorrencias_ativas(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Conta registros da coorte atualmente ativos no cadastro."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_ocorrencias_ativas(inicio, fim)


@tool(args_schema=_ArgumentosPeriodo)
async def obter_taxa_ocorrencias_alta_prioridade(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Calcula a parcela de ocorrências com prioridade alta (código 0)."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_taxa_ocorrencias_alta_prioridade(inicio, fim)


@tool(args_schema=_ArgumentosPeriodoGranularidade)
async def obter_ocorrencias_por_periodo(
    inicio: date,
    fim: date,
    granularidade: Literal["dia", "mes", "ano"],
    runtime: ToolRuntime,
) -> dict:
    """Agrupa ocorrências pela data de criação em dia, mês ou ano."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_ocorrencias_por_periodo(inicio, fim, granularidade)
