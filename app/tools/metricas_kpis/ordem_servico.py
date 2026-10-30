"""Tools gerenciais para métricas e KPIs de ordens de serviço."""

from datetime import date

from langchain.tools import ToolRuntime, tool
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.services.indicadores import ordem_servico as servico
from app.tools.metricas_kpis.contexto import (
    resolver_unidade_indicadores,
)


class _Argumentos(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @model_validator(mode="before")
    @classmethod
    def separar_runtime_injetado(cls, dados):
        if isinstance(dados, dict) and isinstance(dados.get("runtime"), ToolRuntime):
            return {chave: valor for chave, valor in dados.items() if chave != "runtime"}
        return dados


class _ArgumentosPeriodo(_Argumentos):
    inicio: date = Field(
        description="Data inicial inclusiva do período, no formato YYYY-MM-DD.",
    )
    fim: date = Field(
        description=(
            "Data final exclusiva do período, no formato YYYY-MM-DD. "
            "Informe o dia seguinte ao último dia que deve entrar na consulta."
        ),
    )


@tool(args_schema=_ArgumentosPeriodo)
async def obter_total_os(inicio: date, fim: date, runtime: ToolRuntime) -> dict:
    """Conta ordens de serviço criadas no período `[início, fim)`."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_total_os(inicio, fim, unidade_id=unidade_id)
    return {**resultado, "unidade_id": unidade_id}


@tool
async def obter_os_abertas(runtime: ToolRuntime) -> dict:
    """Conta ordens atualmente abertas: atrasadas, pausadas ou em andamento."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_os_abertas(unidade_id=unidade_id)
    return {**resultado, "unidade_id": unidade_id}


@tool
async def obter_os_atrasadas(runtime: ToolRuntime) -> dict:
    """Conta ordens atualmente no status Atrasada; não filtra por período."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_os_atrasadas(unidade_id=unidade_id)
    return {**resultado, "unidade_id": unidade_id}


@tool
async def obter_taxa_atraso_os(runtime: ToolRuntime) -> dict:
    """Calcula a taxa de atraso entre as ordens atualmente abertas."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_taxa_atraso_os(unidade_id=unidade_id)
    return {**resultado, "unidade_id": unidade_id}


@tool(args_schema=_ArgumentosPeriodo)
async def obter_os_finalizadas(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Conta ordens atualmente finalizadas por data de conclusão no período `[início, fim)`."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_os_finalizadas(inicio, fim, unidade_id=unidade_id)
    return {**resultado, "unidade_id": unidade_id}


@tool(args_schema=_ArgumentosPeriodo)
async def obter_taxa_conclusao_prazo(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Calcula a taxa no prazo entre as OS concluídas e elegíveis no período `[início, fim)`."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_taxa_conclusao_prazo(inicio, fim, unidade_id=unidade_id)
    return {**resultado, "unidade_id": unidade_id}


@tool(args_schema=_ArgumentosPeriodo)
async def obter_tempo_medio_espera_os(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Calcula a espera média em minutos das OS criadas no período `[início, fim)`."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_tempo_medio_espera_os(inicio, fim, unidade_id=unidade_id)
    return {**resultado, "unidade_id": unidade_id}


@tool(args_schema=_ArgumentosPeriodo)
async def obter_tempo_medio_resolucao_os(inicio: date, fim: date, runtime: ToolRuntime) -> dict:
    """Calcula tempo de resolucao das OS concluidas no periodo [inicio, fim)."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_tempo_medio_resolucao_os(inicio, fim, unidade_id=unidade_id)
    return {**resultado, "unidade_id": unidade_id}


@tool(args_schema=_ArgumentosPeriodo)
async def obter_tempo_medio_pausado_os(inicio: date, fim: date, runtime: ToolRuntime) -> dict:
    """Calcula tempo pausado medio das OS criadas no periodo [inicio, fim)."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_tempo_medio_pausado_os(inicio, fim, unidade_id=unidade_id)
    return {**resultado, "unidade_id": unidade_id}


@tool(args_schema=_ArgumentosPeriodo)
async def obter_taxa_reabertura_os(inicio: date, fim: date, runtime: ToolRuntime) -> dict:
    """Calcula taxa de OS reabertas na coorte criada em [inicio, fim)."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_taxa_reabertura_os(inicio, fim, unidade_id=unidade_id)
    return {**resultado, "unidade_id": unidade_id}


@tool(args_schema=_ArgumentosPeriodo)
async def obter_taxa_reatribuicao_os(inicio: date, fim: date, runtime: ToolRuntime) -> dict:
    """Calcula taxa de OS reatribuidas na coorte criada em [inicio, fim)."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_taxa_reatribuicao_os(inicio, fim, unidade_id=unidade_id)
    return {**resultado, "unidade_id": unidade_id}


@tool
async def obter_carga_ativa_tecnicos(runtime: ToolRuntime) -> dict:
    """Lista a carga atual de ordens ativas por tecnico, sem periodo."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_carga_ativa_tecnicos(unidade_id=unidade_id)
    return {**resultado, "unidade_id": unidade_id}


@tool(args_schema=_ArgumentosPeriodo)
async def obter_produtividade_tecnicos(inicio: date, fim: date, runtime: ToolRuntime) -> dict:
    """Lista OS finalizadas por tecnico no periodo de conclusao [inicio, fim)."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_produtividade_tecnicos(inicio, fim, unidade_id=unidade_id)
    return {**resultado, "unidade_id": unidade_id}


@tool(args_schema=_ArgumentosPeriodo)
async def obter_media_tarefas_por_os(inicio: date, fim: date, runtime: ToolRuntime) -> dict:
    """Informa indisponibilidade da media de tarefas por OS com tarefas no periodo."""
    unidade_id = await resolver_unidade_indicadores(runtime)
    if isinstance(unidade_id, dict):
        return unidade_id
    resultado = await servico.obter_media_tarefas_por_os(inicio, fim, unidade_id=unidade_id)
    return {**resultado, "unidade_id": unidade_id}
