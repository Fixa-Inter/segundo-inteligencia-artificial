"""Tools gerenciais para métricas e KPIs de problemas/solicitações."""

from datetime import date
from typing import Literal

from langchain.tools import ToolRuntime, tool
from pydantic import Field

from app.services.indicadores import problema as servico
from app.tools.metricas_kpis.ordem_servico import (
    _ArgumentosPeriodo,
    _validar_gestor,
)


class _ArgumentosPeriodoGranularidade(_ArgumentosPeriodo):
    granularidade: Literal["dia", "mes", "ano"] = Field(
        description="Agrupamento temporal: dia, mes ou ano.",
    )


@tool(args_schema=_ArgumentosPeriodo)
async def obter_total_solicitacoes(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Conta solicitações criadas no período [início, fim)."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_total_solicitacoes(inicio, fim)


@tool(args_schema=_ArgumentosPeriodo)
async def obter_solicitacoes_pendentes(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Conta solicitações da coorte que seguem pendentes no snapshot atual."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_solicitacoes_pendentes(inicio, fim)


@tool(args_schema=_ArgumentosPeriodo)
async def obter_solicitacoes_aprovadas(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Conta solicitações da coorte aprovadas no snapshot atual."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_solicitacoes_aprovadas(inicio, fim)


@tool(args_schema=_ArgumentosPeriodo)
async def obter_solicitacoes_reprovadas(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Conta solicitações da coorte reprovadas no snapshot atual."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_solicitacoes_reprovadas(inicio, fim)


@tool(args_schema=_ArgumentosPeriodo)
async def obter_taxa_aprovacao_solicitacoes(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Calcula aprovações como percentual de toda a demanda criada no período."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_taxa_aprovacao_solicitacoes(inicio, fim)


@tool(args_schema=_ArgumentosPeriodo)
async def obter_taxa_reprovacao_solicitacoes(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Calcula reprovações como percentual de toda a demanda criada no período."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_taxa_reprovacao_solicitacoes(inicio, fim)


@tool(args_schema=_ArgumentosPeriodo)
async def obter_taxa_conversao_solicitacoes_os(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Calcula a parcela das solicitações da coorte que gerou OS."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_taxa_conversao_solicitacoes_os(inicio, fim)


@tool(args_schema=_ArgumentosPeriodo)
async def obter_solicitacoes_por_unidade(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Lista o volume da coorte por unidade_id; a gold não fornece nomes."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_solicitacoes_por_unidade(inicio, fim)


@tool(args_schema=_ArgumentosPeriodo)
async def obter_solicitacoes_por_local(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Lista o volume da coorte por local_id; a gold não fornece nomes ou tipos."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_solicitacoes_por_local(inicio, fim)


@tool(args_schema=_ArgumentosPeriodo)
async def obter_solicitacoes_por_categoria_equipamento(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Lista solicitações por categoria de equipamento, não de problema."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_solicitacoes_por_categoria_equipamento(inicio, fim)


@tool(args_schema=_ArgumentosPeriodoGranularidade)
async def obter_solicitacoes_por_periodo(
    inicio: date,
    fim: date,
    granularidade: Literal["dia", "mes", "ano"],
    runtime: ToolRuntime,
) -> dict:
    """Agrupa solicitações por início de dia, mês ou ano."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_solicitacoes_por_periodo(inicio, fim, granularidade)


@tool(args_schema=_ArgumentosPeriodo)
async def obter_taxa_recorrencia_local_categoria(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Calcula episódios recorrentes por local e categoria em [início, fim)."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_taxa_recorrencia_local_categoria(inicio, fim)
