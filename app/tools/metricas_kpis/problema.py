"""Tools gerenciais para métricas e KPIs de problemas/solicitações."""

from datetime import date
from typing import Literal

from langchain.tools import ToolRuntime, tool
from pydantic import Field

from app.services.indicadores import problema as servico
from app.tools.metricas_kpis.contexto import resolver_unidade_indicadores
from app.tools.metricas_kpis.ordem_servico import (
    _ArgumentosPeriodo,
)


class _ArgumentosPeriodoGranularidade(_ArgumentosPeriodo):
    granularidade: Literal["dia", "mes", "ano"] = Field(
        description="Agrupamento temporal: dia, mes ou ano.",
    )


@tool(args_schema=_ArgumentosPeriodo)
async def obter_total_solicitacoes(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Conta solicitações criadas em [início, fim) na unidade autenticada."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_total_solicitacoes(
        inicio, fim, unidade_id=unidade_id,
    )
    return {**resultado, "unidade_id": unidade_id}


@tool(args_schema=_ArgumentosPeriodo)
async def obter_solicitacoes_pendentes(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Conta solicitações do período pendentes na última atualização da unidade."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_solicitacoes_pendentes(
        inicio, fim, unidade_id=unidade_id,
    )
    return {**resultado, "unidade_id": unidade_id}


@tool(args_schema=_ArgumentosPeriodo)
async def obter_solicitacoes_aprovadas(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Conta solicitações do período aprovadas na última atualização da unidade."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_solicitacoes_aprovadas(
        inicio, fim, unidade_id=unidade_id,
    )
    return {**resultado, "unidade_id": unidade_id}


@tool(args_schema=_ArgumentosPeriodo)
async def obter_solicitacoes_reprovadas(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Conta solicitações do período reprovadas na última atualização da unidade."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_solicitacoes_reprovadas(
        inicio, fim, unidade_id=unidade_id,
    )
    return {**resultado, "unidade_id": unidade_id}


@tool(args_schema=_ArgumentosPeriodo)
async def obter_taxa_aprovacao_solicitacoes(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Calcula aprovações como percentual de toda a demanda criada no período."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_taxa_aprovacao_solicitacoes(
        inicio, fim, unidade_id=unidade_id,
    )
    return {**resultado, "unidade_id": unidade_id}


@tool(args_schema=_ArgumentosPeriodo)
async def obter_taxa_reprovacao_solicitacoes(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Calcula reprovações como percentual de toda a demanda criada no período."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_taxa_reprovacao_solicitacoes(
        inicio, fim, unidade_id=unidade_id,
    )
    return {**resultado, "unidade_id": unidade_id}


@tool(args_schema=_ArgumentosPeriodo)
async def obter_taxa_conversao_solicitacoes_os(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Calcula a parcela das solicitações da coorte que gerou OS."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_taxa_conversao_solicitacoes_os(
        inicio, fim, unidade_id=unidade_id,
    )
    return {**resultado, "unidade_id": unidade_id}


@tool(args_schema=_ArgumentosPeriodo)
async def obter_solicitacoes_por_unidade(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Retorna o volume do período somente da unidade autenticada, sem nome."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_solicitacoes_por_unidade(
        inicio, fim, unidade_id=unidade_id,
    )
    return {**resultado, "unidade_id": unidade_id}


@tool(args_schema=_ArgumentosPeriodo)
async def obter_solicitacoes_por_local(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Lista o volume da coorte por local_id; a gold não fornece nomes ou tipos."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_solicitacoes_por_local(
        inicio, fim, unidade_id=unidade_id,
    )
    return {**resultado, "unidade_id": unidade_id}


@tool(args_schema=_ArgumentosPeriodo)
async def obter_solicitacoes_por_categoria_equipamento(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Lista solicitações por categoria de equipamento, não de problema."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_solicitacoes_por_categoria_equipamento(
        inicio, fim, unidade_id=unidade_id,
    )
    return {**resultado, "unidade_id": unidade_id}


@tool(args_schema=_ArgumentosPeriodoGranularidade)
async def obter_solicitacoes_por_periodo(
    inicio: date,
    fim: date,
    granularidade: Literal["dia", "mes", "ano"],
    runtime: ToolRuntime,
) -> dict:
    """Agrupa solicitações por início de dia, mês ou ano."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_solicitacoes_por_periodo(
        inicio, fim, granularidade, unidade_id=unidade_id,
    )
    return {**resultado, "unidade_id": unidade_id}


@tool(args_schema=_ArgumentosPeriodo)
async def obter_taxa_recorrencia_local_categoria(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Consulta recorrência do BI por local/categoria da unidade, pelo início do episódio."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_taxa_recorrencia_local_categoria(
        inicio, fim, unidade_id=unidade_id,
    )
    return {**resultado, "unidade_id": unidade_id}
