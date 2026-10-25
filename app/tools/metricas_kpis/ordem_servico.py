"""Tools gerenciais para métricas e KPIs de ordens de serviço."""

from datetime import date

from langchain.tools import ToolRuntime, tool
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas import UsuarioContexto
from app.services.indicadores import ordem_servico as servico


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


def _validar_gestor(runtime: ToolRuntime) -> dict | None:
    contexto = runtime.context
    if not isinstance(contexto, dict) or not isinstance(
        contexto.get("usuario"), UsuarioContexto,
    ):
        return {
            "status": "ACESSO_NEGADO",
            "mensagem": "Contexto autenticado indisponível para consultar indicadores.",
        }

    usuario = contexto["usuario"]
    if usuario.tipo_acesso != "gestor":
        return {
            "status": "ACESSO_NEGADO",
            "mensagem": "Somente gestores podem consultar indicadores de ordens de serviço.",
        }
    return None


@tool(args_schema=_ArgumentosPeriodo)
async def obter_total_os(inicio: date, fim: date, runtime: ToolRuntime) -> dict:
    """Conta ordens de serviço criadas no período `[início, fim)`."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_total_os(inicio, fim)


@tool
async def obter_os_abertas(runtime: ToolRuntime) -> dict:
    """Conta ordens atualmente abertas: atrasadas, pausadas ou em andamento."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_os_abertas()


@tool
async def obter_os_atrasadas(runtime: ToolRuntime) -> dict:
    """Conta ordens atualmente no status Atrasada; não filtra por período."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_os_atrasadas()


@tool
async def obter_taxa_atraso_os(runtime: ToolRuntime) -> dict:
    """Calcula a taxa de atraso entre as ordens atualmente abertas."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_taxa_atraso_os()


@tool(args_schema=_ArgumentosPeriodo)
async def obter_os_finalizadas(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Conta ordens atualmente finalizadas por data de conclusão no período `[início, fim)`."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_os_finalizadas(inicio, fim)


@tool(args_schema=_ArgumentosPeriodo)
async def obter_taxa_conclusao_prazo(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Calcula a taxa no prazo entre as OS concluídas e elegíveis no período `[início, fim)`."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_taxa_conclusao_prazo(inicio, fim)


@tool(args_schema=_ArgumentosPeriodo)
async def obter_tempo_medio_espera_os(
    inicio: date, fim: date, runtime: ToolRuntime,
) -> dict:
    """Calcula a espera média em minutos das OS criadas no período `[início, fim)`."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_tempo_medio_espera_os(inicio, fim)
@tool(args_schema=_ArgumentosPeriodo)
async def obter_tempo_medio_resolucao_os(inicio: date, fim: date, runtime: ToolRuntime) -> dict:
    """Calcula tempo de resolucao das OS concluidas no periodo [inicio, fim)."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_tempo_medio_resolucao_os(inicio, fim)


@tool(args_schema=_ArgumentosPeriodo)
async def obter_tempo_medio_pausado_os(inicio: date, fim: date, runtime: ToolRuntime) -> dict:
    """Calcula tempo pausado medio das OS criadas no periodo [inicio, fim)."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_tempo_medio_pausado_os(inicio, fim)


@tool(args_schema=_ArgumentosPeriodo)
async def obter_taxa_reabertura_os(inicio: date, fim: date, runtime: ToolRuntime) -> dict:
    """Calcula taxa de OS reabertas na coorte criada em [inicio, fim)."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_taxa_reabertura_os(inicio, fim)


@tool(args_schema=_ArgumentosPeriodo)
async def obter_taxa_reatribuicao_os(inicio: date, fim: date, runtime: ToolRuntime) -> dict:
    """Calcula taxa de OS reatribuidas na coorte criada em [inicio, fim)."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_taxa_reatribuicao_os(inicio, fim)


@tool
async def obter_carga_ativa_tecnicos(runtime: ToolRuntime) -> dict:
    """Lista a carga atual de ordens ativas por tecnico, sem periodo."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_carga_ativa_tecnicos()


@tool(args_schema=_ArgumentosPeriodo)
async def obter_produtividade_tecnicos(inicio: date, fim: date, runtime: ToolRuntime) -> dict:
    """Lista OS finalizadas por tecnico no periodo de conclusao [inicio, fim)."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_produtividade_tecnicos(inicio, fim)


@tool(args_schema=_ArgumentosPeriodo)
async def obter_media_tarefas_por_os(inicio: date, fim: date, runtime: ToolRuntime) -> dict:
    """Calcula media ponderada de tarefas por OS criada em [inicio, fim)."""
    negado = _validar_gestor(runtime)
    if negado:
        return negado
    return await servico.obter_media_tarefas_por_os(inicio, fim)
