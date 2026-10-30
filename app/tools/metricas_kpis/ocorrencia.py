"""Tools gerenciais para métricas de ocorrências."""

from datetime import date
from typing import Literal

from langchain.tools import ToolRuntime, tool
from pydantic import Field

from app.services.indicadores import ocorrencia as servico
from app.tools.metricas_kpis.contexto import resolver_unidade_indicadores
from app.tools.metricas_kpis.ordem_servico import (
    _ArgumentosPeriodo,
)


class _ArgumentosPeriodoGranularidade(_ArgumentosPeriodo):
    granularidade: Literal["dia", "mes", "ano"] = Field(
        description="Agrupamento temporal: dia, mes ou ano.",
    )


@tool(args_schema=_ArgumentosPeriodo)
async def obter_total_ocorrencias(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Conta ocorrências criadas em [início, fim) na unidade autenticada."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_total_ocorrencias(
        inicio, fim, unidade_id=unidade_id,
    )
    return {**resultado, "unidade_id": unidade_id}


@tool(args_schema=_ArgumentosPeriodo)
async def obter_ocorrencias_por_tecnico(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Lista o volume de ocorrências criadas por técnico no período."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_ocorrencias_por_tecnico(
        inicio, fim, unidade_id=unidade_id,
    )
    return {**resultado, "unidade_id": unidade_id}


@tool(args_schema=_ArgumentosPeriodo)
async def obter_ocorrencias_por_unidade(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Retorna o volume de ocorrências do período somente da unidade autenticada."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_ocorrencias_por_unidade(
        inicio, fim, unidade_id=unidade_id,
    )
    return {**resultado, "unidade_id": unidade_id}


@tool(args_schema=_ArgumentosPeriodo)
async def obter_ocorrencias_por_local(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Lista o volume de ocorrências criadas por local no período."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_ocorrencias_por_local(
        inicio, fim, unidade_id=unidade_id,
    )
    return {**resultado, "unidade_id": unidade_id}


@tool(args_schema=_ArgumentosPeriodo)
async def obter_ocorrencias_por_categoria_problema(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Lista ocorrências por categoria de problema no período."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_ocorrencias_por_categoria_problema(
        inicio, fim, unidade_id=unidade_id,
    )
    return {**resultado, "unidade_id": unidade_id}


@tool(args_schema=_ArgumentosPeriodo)
async def obter_ocorrencias_por_categoria_equipamento(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Lista ocorrências agrupadas por categoria de equipamento."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_ocorrencias_por_categoria_equipamento(
        inicio, fim, unidade_id=unidade_id,
    )
    return {**resultado, "unidade_id": unidade_id}


@tool(args_schema=_ArgumentosPeriodo)
async def obter_ocorrencias_por_prioridade(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Lista ocorrências por prioridade: alta 0, média 1, baixa 2."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_ocorrencias_por_prioridade(
        inicio, fim, unidade_id=unidade_id,
    )
    return {**resultado, "unidade_id": unidade_id}


@tool(args_schema=_ArgumentosPeriodo)
async def obter_ocorrencias_ativas(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Conta ocorrências do período aguardando revisão/aprovação do gestor na unidade."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_ocorrencias_ativas(
        inicio, fim, unidade_id=unidade_id,
    )
    return {**resultado, "unidade_id": unidade_id}


@tool(args_schema=_ArgumentosPeriodo)
async def obter_taxa_ocorrencias_alta_prioridade(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Calcula a parcela de ocorrências com prioridade alta (código 0)."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_taxa_ocorrencias_alta_prioridade(
        inicio, fim, unidade_id=unidade_id,
    )
    return {**resultado, "unidade_id": unidade_id}


@tool(args_schema=_ArgumentosPeriodoGranularidade)
async def obter_ocorrencias_por_periodo(
    inicio: date,
    fim: date,
    granularidade: Literal["dia", "mes", "ano"],
    runtime: ToolRuntime,
) -> dict:
    """Agrupa ocorrências pela data de criação em dia, mês ou ano."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_ocorrencias_por_periodo(
        inicio, fim, granularidade, unidade_id=unidade_id,
    )
    return {**resultado, "unidade_id": unidade_id}
