"""Adaptação de schemas e execução das tools; regras analíticas ficam nos serviços."""

import logging
from typing import Literal

from langchain.tools import ToolRuntime, tool
from pydantic import BaseModel, Field, ValidationError, create_model, model_validator

from app.schemas.visualizacao import (
    ConsultaVisualizacaoPeriodo, ConsultaVisualizacaoSnapshot, GranularidadeTemporal,
    PeriodoVisualizacao, ResultadoConsultaVisualizacao, SelecaoFiltro,
)
from app.services.visualizacoes.captura import CapturaExecucaoVisualizacao
from app.services.visualizacoes.validacao import validar_resultado_consulta
from app.observability.metricas import BYTES_VISUALIZACAO
from .contexto import resolver_unidade, validar_acesso
from .filtros import validar_consulta


registrador = logging.getLogger(__name__)


class _RuntimeInjetado(BaseModel):
    @model_validator(mode="before")
    @classmethod
    def separar_runtime(cls, dados):
        # ToolNode injeta o objeto Python; um runtime recebido como JSON não é
        # removido e continua sendo um campo extra inválido.
        if isinstance(dados, dict) and isinstance(dados.get("runtime"), ToolRuntime):
            return {chave: valor for chave, valor in dados.items() if chave != "runtime"}
        return dados


def _erro_validacao():
    return ResultadoConsultaVisualizacao(
        status="ERRO_VALIDACAO", mensagem="Confira a análise, o período, a granularidade e os filtros da ferramenta.",
    )


def _tratar_validacao(_erro):
    # ValidationError pode incluir valores recebidos e o contexto injetado.
    return _erro_validacao().model_dump_json()


async def _executar(dominio, runtime, dados):
    negado = validar_acesso(runtime)
    if negado is not None:
        return negado.model_dump(mode="json")
    try:
        contrato = ConsultaVisualizacaoSnapshot if dominio.FONTE.campo_periodo is None else ConsultaVisualizacaoPeriodo
        consulta = contrato.model_validate(dados)
        consulta = contrato.model_validate(consulta.model_dump())
        analise = validar_consulta(consulta, fonte_id=dominio.FONTE.id)
    except (ValidationError, TypeError):
        return _erro_validacao().model_dump(mode="json")
    except ValueError as erro:
        return ResultadoConsultaVisualizacao(status="ERRO_VALIDACAO", mensagem=str(erro)).model_dump(mode="json")

    try:
        unidade_id = await resolver_unidade(runtime)
        if isinstance(unidade_id, ResultadoConsultaVisualizacao):
            return unidade_id.model_dump(mode="json")
        resultado = await dominio.consultar(consulta, unidade_id=unidade_id)
        resultado = validar_resultado_consulta(consulta, analise, unidade_id, resultado)
        captura = runtime.context.get("captura_visualizacao")
        if captura is not None:
            if not isinstance(captura, CapturaExecucaoVisualizacao):
                raise ValueError("Contexto de captura inválido.")
            captura.registrar(
                runtime.context, runtime.tool_call_id,
                f"consultar_visualizacao_{dominio.FONTE.id}", consulta, unidade_id, resultado,
            )
        BYTES_VISUALIZACAO.labels("tool").observe(len(resultado.model_dump_json().encode("utf-8")))
        return resultado.model_dump(mode="json")
    except Exception as erro:
        registrador.error("Falha na ferramenta de visualização %s: %s", dominio.FONTE.id, type(erro).__name__)
        return ResultadoConsultaVisualizacao(
            status="ERRO_FERRAMENTA", mensagem="Não foi possível obter um resultado válido para a visualização.",
        ).model_dump(mode="json")


def criar_tool(dominio):
    """Vincula uma tool a referências canônicas, sem duplicar o catálogo."""
    snapshot = dominio.FONTE.campo_periodo is None
    contrato = ConsultaVisualizacaoSnapshot if snapshot else ConsultaVisualizacaoPeriodo
    identificadores = tuple(analise.id for analise in dominio.ANALISES)
    argumentos = create_model(
        f"ArgumentosVisualizacao_{dominio.FONTE.id}",
        __base__=(contrato, _RuntimeInjetado),
        analise_id=(Literal[identificadores], Field(description="Análise desta fonte.")),
        filtros=(dict[str, SelecaoFiltro], Field(
            default_factory=dict, description="Campos permitidos: " + ", ".join(dominio.FILTROS),
        )),
    )
    descricao = (
        "Consulta dados analíticos de visualização da unidade autenticada do gestor ou administrador. "
        + ("Snapshot atual, sem período ou granularidade. " if snapshot else
           "Informe período com início inclusivo e fim exclusivo; séries exigem dia, semana ou mes. ")
        + "Análises: " + "; ".join(f"{a.id}: {a.titulo}" for a in dominio.ANALISES)
        + ". Retorna dados, cobertura, metadados e status; não configura o gráfico."
    )
    if snapshot:
        async def consultar(analise_id: str, runtime: ToolRuntime = None, filtros: dict[str, SelecaoFiltro] | None = None) -> dict:
            return await _executar(dominio, runtime, {"analise_id": analise_id, "filtros": filtros if filtros is not None else {}})
    else:
        async def consultar(
            analise_id: str, periodo: PeriodoVisualizacao, runtime: ToolRuntime = None,
            granularidade: GranularidadeTemporal | None = None, filtros: dict[str, SelecaoFiltro] | None = None,
        ) -> dict:
            return await _executar(dominio, runtime, {
                "analise_id": analise_id, "periodo": periodo, "granularidade": granularidade,
                "filtros": filtros if filtros is not None else {},
            })
    ferramenta = tool(
        f"consultar_visualizacao_{dominio.FONTE.id}", args_schema=argumentos, description=descricao,
    )(consultar)
    ferramenta.handle_validation_error = _tratar_validacao
    return ferramenta
