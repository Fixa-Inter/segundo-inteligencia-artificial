"""Contratos internos de consulta, definições e resultados de visualização.

Os serviços preenchem estes contratos com as regras de cada domínio. O contrato
público transporta dados analíticos, sem opções de renderização Recharts.
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Annotated, Literal

from pydantic import (
    BaseModel, ConfigDict, Field, StrictBool, StrictFloat, StrictInt, StrictStr,
    field_validator, model_validator,
)


FormatoDados = Literal["serie_temporal", "categorias", "histograma", "boxplot"]
Agregacao = Literal["SUM", "COUNT", "AVG"]


@dataclass(frozen=True)
class Fonte:
    id: str
    tabela: str
    chave: tuple[str, ...]
    campo_periodo: str | None
    campo_snapshot: str | None
    ids_textuais: frozenset[str] = frozenset()


@dataclass(frozen=True)
class FiltroObrigatorio:
    campo: str
    valor: int | bool


@dataclass(frozen=True)
class Analise:
    id: str
    titulo: str
    fonte: Fonte
    formato_dados: FormatoDados
    dimensoes: tuple[str, ...]
    campo_valor: str
    agregacao: Agregacao | None
    unidade_medida: Literal["quantidade", "minutos", "percentual"]
    excluir_nulos: bool = False
    filtros_obrigatorios: tuple[FiltroObrigatorio, ...] = ()
    escala_percentual: Literal[100] | None = None
    excluir_negativos: bool = False


class ResumoGrupoPequeno(BaseModel):
    """Dados analíticos de um grupo; o serviço decide quando usar o resumo."""

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    tipo: Literal["resumo"] = "resumo"
    analise_id: str
    grupo: dict[str, StrictInt | StrictStr | None]
    unidade: Literal["minutos"] = "minutos"
    qtd_registros: int = Field(ge=1, strict=True)
    minimo: float
    maximo: float
    media: float
    mediana: float
    motivo: Literal["POUCOS_REGISTROS_PARA_BOXPLOT"] = "POUCOS_REGISTROS_PARA_BOXPLOT"
    base_calculo: "BaseCalculoVisualizacao | None" = None

    @model_validator(mode="after")
    def validar_estatisticas(self):
        if self.base_calculo is not None and self.qtd_registros != self.base_calculo.qtd_registros_elegiveis:
            raise ValueError("A quantidade do resumo deve corresponder à base elegível.")
        if not (
            self.minimo <= self.media <= self.maximo
            and self.minimo <= self.mediana <= self.maximo
        ):
            raise ValueError("Média e mediana devem estar entre mínimo e máximo.")
        return self


ValorFiltro = StrictInt | StrictStr | StrictBool
SelecaoFiltro = ValorFiltro | Annotated[list[ValorFiltro], Field(min_length=1)]
DimensoesGrupo = dict[str, StrictInt | StrictStr | None]
ValorMedida = StrictInt | StrictFloat | None
GranularidadeTemporal = Literal["dia", "semana", "mes"]


class _ContratoVisualizacao(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class PeriodoVisualizacao(_ContratoVisualizacao):
    inicio: date = Field(description="Data inicial inclusiva (YYYY-MM-DD).")
    fim: date = Field(description="Data final exclusiva (YYYY-MM-DD).")

    @field_validator("inicio", "fim", mode="before")
    @classmethod
    def validar_formato_data(cls, valor):
        if type(valor) is date:
            return valor
        if isinstance(valor, str) and len(valor) == 10 and valor[4] == valor[7] == "-":
            return date.fromisoformat(valor)
        raise ValueError("Informe a data no formato YYYY-MM-DD.")

    @model_validator(mode="after")
    def validar_intervalo(self):
        if self.inicio >= self.fim:
            raise ValueError("O início deve ser anterior ao fim exclusivo do período.")
        return self


class _ConsultaVisualizacao(_ContratoVisualizacao):
    analise_id: str = Field(pattern=r"^VIS-\d{2}$")
    filtros: dict[str, SelecaoFiltro] = Field(default_factory=dict)


class ConsultaVisualizacaoPeriodo(_ConsultaVisualizacao):
    periodo: PeriodoVisualizacao
    granularidade: GranularidadeTemporal | None = None


class ConsultaVisualizacaoSnapshot(_ConsultaVisualizacao):
    """Snapshot não oferece campos de período ou granularidade."""


class ReferenciaVisualizacao(_ContratoVisualizacao):
    """Seleção interna de um resultado; dados e renderização não vêm do LLM."""

    analise_id: str = Field(pattern=r"^VIS-\d{2}$")
    consulta_id: StrictStr = Field(min_length=1)

    @field_validator("consulta_id")
    @classmethod
    def validar_identificador(cls, valor):
        if not valor.strip() or valor != valor.strip():
            raise ValueError("A referência deve preservar o identificador retornado pela tool.")
        return valor


class BaseCalculoVisualizacao(_ContratoVisualizacao):
    """Cobertura da medida dentro do recorte de unidade, período e filtros.

    O total antecede os critérios de elegibilidade da medida. A cobertura pode
    ser obtida pela razão elegíveis/total; total zero significa ausência de base.
    """

    qtd_registros_total: int = Field(ge=0, strict=True)
    qtd_registros_elegiveis: int = Field(ge=0, strict=True)
    qtd_tempos_negativos_excluidos: int = Field(default=0, ge=0, strict=True)

    @model_validator(mode="after")
    def validar_quantidades(self):
        if self.qtd_registros_elegiveis + self.qtd_tempos_negativos_excluidos > self.qtd_registros_total:
            raise ValueError("Elegíveis e negativos excluídos não podem exceder o total.")
        return self


class PontoCategoria(_ContratoVisualizacao):
    grupo: DimensoesGrupo
    valor: ValorMedida
    qtd_registros: int = Field(ge=0, strict=True)
    base_calculo: BaseCalculoVisualizacao | None = None

    @model_validator(mode="after")
    def validar_base_calculo(self):
        if self.base_calculo is not None:
            if self.qtd_registros != self.base_calculo.qtd_registros_elegiveis:
                raise ValueError("A quantidade do ponto deve corresponder à base elegível.")
            if (self.valor is None) != (self.qtd_registros == 0):
                raise ValueError("Uma medida sem base deve ser nula; medida com base exige valor.")
        return self


class PeriodoSerieTemporal(_ContratoVisualizacao):
    """Intervalo do calendário e sua interseção com o pedido; fins exclusivos."""

    calendario: PeriodoVisualizacao
    consultado: PeriodoVisualizacao
    parcial: StrictBool

    @model_validator(mode="after")
    def validar_recorte(self):
        if not (
            self.calendario.inicio <= self.consultado.inicio
            and self.consultado.fim <= self.calendario.fim
        ):
            raise ValueError("O trecho consultado deve estar contido no período do calendário.")
        if self.parcial != (self.calendario != self.consultado):
            raise ValueError("A indicação de período parcial deve corresponder ao trecho consultado.")
        return self


class PontoSerieTemporal(PontoCategoria):
    data_referencia: date
    periodo: PeriodoSerieTemporal | None = None

    @model_validator(mode="after")
    def validar_referencia_periodo(self):
        if self.periodo is not None and self.data_referencia != self.periodo.calendario.inicio:
            raise ValueError("A data de referência deve identificar o início do período do calendário.")
        return self


class DadosCategorias(_ContratoVisualizacao):
    tipo: Literal["categorias"] = "categorias"
    pontos: list[PontoCategoria] = Field(min_length=1)


class DadosSerieTemporal(_ContratoVisualizacao):
    tipo: Literal["serie_temporal"] = "serie_temporal"
    pontos: list[PontoSerieTemporal] = Field(min_length=1)


class IntervaloHistograma(_ContratoVisualizacao):
    inferior: float
    superior: float
    frequencia: int = Field(ge=0, strict=True)
    inclui_superior: bool

    @model_validator(mode="after")
    def validar_limites(self):
        if self.inferior > self.superior:
            raise ValueError("O limite inferior não pode exceder o superior.")
        return self


class DadosHistograma(_ContratoVisualizacao):
    tipo: Literal["histograma"] = "histograma"
    intervalos: list[IntervaloHistograma] = Field(min_length=1)
    qtd_registros: int = Field(ge=1, strict=True)

    @model_validator(mode="after")
    def validar_frequencias(self):
        if sum(intervalo.frequencia for intervalo in self.intervalos) != self.qtd_registros:
            raise ValueError("As frequências devem cobrir a população do histograma.")
        return self


class GrupoBoxplot(_ContratoVisualizacao):
    tipo: Literal["boxplot"] = "boxplot"
    analise_id: str
    grupo: DimensoesGrupo
    unidade: Literal["minutos"] = "minutos"
    qtd_registros: int = Field(ge=1, strict=True)
    minimo: float
    q1: float
    mediana: float
    q3: float
    maximo: float
    limite_inferior: float
    limite_superior: float
    bigode_inferior: float
    bigode_superior: float
    valores_extremos: list[float] = Field(default_factory=list)
    qtd_extremos_total: int = Field(ge=0, strict=True)
    qtd_extremos_omitidos: int = Field(ge=0, strict=True)
    base_calculo: BaseCalculoVisualizacao | None = None

    @model_validator(mode="after")
    def validar_estatisticas(self):
        if self.base_calculo is not None and self.qtd_registros != self.base_calculo.qtd_registros_elegiveis:
            raise ValueError("A quantidade do boxplot deve corresponder à base elegível.")
        if not self.minimo <= self.q1 <= self.mediana <= self.q3 <= self.maximo:
            raise ValueError("Os quartis devem estar ordenados entre mínimo e máximo.")
        if not (
            self.minimo <= self.bigode_inferior <= self.bigode_superior <= self.maximo
            and self.limite_inferior <= self.bigode_inferior
            and self.bigode_superior <= self.limite_superior
        ):
            raise ValueError("Bigodes devem representar valores dentro dos limites.")
        if not (
            len(self.valores_extremos) + self.qtd_extremos_omitidos == self.qtd_extremos_total
            and self.qtd_extremos_total <= self.qtd_registros
        ):
            raise ValueError("As contagens de pontos extremos são inconsistentes.")
        if any(
            not self.minimo <= valor <= self.maximo
            or self.limite_inferior <= valor <= self.limite_superior
            for valor in self.valores_extremos
        ):
            raise ValueError("Pontos extremos devem estar fora dos limites do boxplot.")
        return self


class GrupoSemBaseBoxplot(_ContratoVisualizacao):
    """Preserva um grupo observado sem inventar estatísticas ou um resumo."""

    tipo: Literal["sem_base"] = "sem_base"
    analise_id: str
    grupo: DimensoesGrupo
    unidade: Literal["minutos"] = "minutos"
    qtd_registros: int = Field(default=0, ge=0, le=0, strict=True)
    motivo: Literal["SEM_OBSERVACOES_ELEGIVEIS"] = "SEM_OBSERVACOES_ELEGIVEIS"
    base_calculo: BaseCalculoVisualizacao

    @model_validator(mode="after")
    def validar_base(self):
        if self.base_calculo.qtd_registros_elegiveis or not self.base_calculo.qtd_registros_total:
            raise ValueError("Um grupo sem base exige registros observados e nenhum elegível.")
        return self


ResultadoGrupoBoxplot = Annotated[
    GrupoBoxplot | ResumoGrupoPequeno | GrupoSemBaseBoxplot, Field(discriminator="tipo"),
]


class DadosBoxplot(_ContratoVisualizacao):
    tipo: Literal["boxplot"] = "boxplot"
    grupos: list[ResultadoGrupoBoxplot] = Field(min_length=1)


DadosVisualizacao = Annotated[
    DadosCategorias | DadosSerieTemporal | DadosHistograma | DadosBoxplot,
    Field(discriminator="tipo"),
]


class MetadadosConsultaVisualizacao(_ContratoVisualizacao):
    analise_id: str
    fonte: str
    formato_dados: FormatoDados
    campo_valor: str
    agregacao: Agregacao | None
    unidade_medida: Literal["quantidade", "minutos", "percentual"]
    escala_percentual: Literal[100] | None = None
    periodo: PeriodoVisualizacao | None = None
    granularidade: GranularidadeTemporal | None = None
    instante_snapshot: datetime | None = None
    consultado_em: datetime
    consulta_id: str
    filtros_solicitados: dict[str, SelecaoFiltro] = Field(default_factory=dict)
    filtros_aplicados: dict[str, SelecaoFiltro] = Field(default_factory=dict)
    filtros_nao_aplicados: list[str] = Field(default_factory=list)
    qtd_registros_considerados: int = Field(ge=0, strict=True)
    base_calculo: BaseCalculoVisualizacao | None = None

    @field_validator("consultado_em")
    @classmethod
    def validar_fuso_consulta(cls, valor):
        if valor.tzinfo is None or valor.utcoffset() is None:
            raise ValueError("O instante da consulta deve informar o fuso horário.")
        return valor

    @model_validator(mode="after")
    def validar_referencia_temporal(self):
        if self.base_calculo is not None and (
            self.qtd_registros_considerados != self.base_calculo.qtd_registros_elegiveis
        ):
            raise ValueError("A quantidade considerada deve corresponder à base elegível.")
        if self.periodo is not None and self.instante_snapshot is not None:
            raise ValueError("Uma consulta não pode representar período e snapshot simultaneamente.")
        if self.granularidade is not None and self.periodo is None:
            raise ValueError("Granularidade temporal exige um período.")
        return self


StatusConsultaVisualizacao = Literal[
    "SUCESSO", "SUCESSO_PARCIAL", "SEM_RESULTADO", "SEM_BASE_CALCULO",
    "ERRO_VALIDACAO", "ACESSO_NEGADO", "ERRO_FERRAMENTA", "TIMEOUT",
    "RESULTADO_TRUNCADO",
]

StatusVisualizacao = Literal[StatusConsultaVisualizacao, "AGUARDANDO_INFORMACAO", "ERRO_MODELO"]


class ResultadoConsultaVisualizacao(_ContratoVisualizacao):
    """Retorno analítico interno das tools, sem configuração de renderização."""

    versao_contrato: Literal["1.0"] = "1.0"
    status: StatusConsultaVisualizacao
    mensagem: str = Field(min_length=1)
    metadados: MetadadosConsultaVisualizacao | None = None
    dados: DadosVisualizacao | None = None
    avisos: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validar_conteudo(self):
        sucesso = self.status in {"SUCESSO", "SUCESSO_PARCIAL"}
        if sucesso and (self.dados is None or self.metadados is None):
            raise ValueError("Sucesso exige dados e metadados da consulta.")
        if not sucesso and self.dados is not None:
            raise ValueError("Resultados sem sucesso não podem liberar dados de gráfico.")
        if self.dados is not None and self.metadados is not None:
            if self.dados.tipo != self.metadados.formato_dados:
                raise ValueError("O formato dos dados não corresponde aos metadados.")
            if isinstance(self.dados, DadosSerieTemporal):
                for ponto in self.dados.pontos:
                    if ponto.periodo is None:
                        continue
                    periodo = self.metadados.periodo
                    calendario = ponto.periodo.calendario
                    if periodo is None or (
                        ponto.periodo.consultado.inicio != max(periodo.inicio, calendario.inicio)
                        or ponto.periodo.consultado.fim != min(periodo.fim, calendario.fim)
                    ):
                        raise ValueError("O trecho do ponto deve coincidir com o recorte dos metadados.")
            if isinstance(self.dados, DadosBoxplot) and any(
                grupo.analise_id != self.metadados.analise_id for grupo in self.dados.grupos
            ):
                raise ValueError("Os grupos devem pertencer à análise da consulta.")
        return self


class ConsultaVisualizacaoCapturada(_ContratoVisualizacao):
    """Registro interno do servidor; não representa aprovação ou payload público."""

    execucao_id: StrictStr = Field(min_length=1)
    turno_id: StrictStr = Field(min_length=1)
    sessao_id: StrictStr = Field(min_length=1)
    usuario_id: int = Field(gt=0, strict=True)
    chamada_id: StrictStr = Field(min_length=1)
    ferramenta: StrictStr = Field(min_length=1)
    unidade_id: int = Field(gt=0, strict=True)
    consulta: ConsultaVisualizacaoPeriodo | ConsultaVisualizacaoSnapshot
    resultado: ResultadoConsultaVisualizacao


class AprovacaoVisualizacao(_ContratoVisualizacao):
    """Vínculo interno com o conteúdo exato avaliado pelo juiz."""

    texto_avaliado: StrictStr = Field(min_length=1)
    conteudo_sha256: StrictStr = Field(pattern=r"^[a-f0-9]{64}$")


class MetadadosVisualizacaoPublica(_ContratoVisualizacao):
    analise_id: StrictStr = Field(pattern=r"^VIS-\d{2}$")
    unidade_id: int = Field(gt=0, strict=True)
    unidade_medida: Literal["quantidade", "minutos", "percentual"]
    escala_percentual: Literal[100] | None = None
    periodo: PeriodoVisualizacao | None = None
    granularidade: GranularidadeTemporal | None = None
    instante_snapshot: datetime | None = None
    consultado_em: datetime
    filtros: dict[str, SelecaoFiltro] = Field(default_factory=dict)
    qtd_registros_considerados: int = Field(ge=0, strict=True)
    base_calculo: BaseCalculoVisualizacao | None = None

    @field_validator("consultado_em")
    @classmethod
    def validar_fuso(cls, valor):
        if valor.tzinfo is None or valor.utcoffset() is None:
            raise ValueError("O instante da consulta exige fuso horário.")
        return valor

    @model_validator(mode="after")
    def validar_metadados(self):
        if self.periodo is not None and self.instante_snapshot is not None:
            raise ValueError("Período e snapshot não podem coexistir.")
        if self.granularidade is not None and self.periodo is None:
            raise ValueError("Granularidade exige período.")
        if self.base_calculo is not None and self.qtd_registros_considerados != self.base_calculo.qtd_registros_elegiveis:
            raise ValueError("Quantidade incompatível com a base elegível.")
        return self


class VisualizacaoPublica(_ContratoVisualizacao):
    """Conteúdo versionado salvo junto da mensagem e devolvido sem recálculo."""

    versao_contrato: Literal["1.0"] = "1.0"
    visualizacao_id: StrictStr = Field(min_length=1)
    titulo: StrictStr = Field(min_length=1)
    status: Literal["SUCESSO", "SUCESSO_PARCIAL"]
    metadados: MetadadosVisualizacaoPublica
    dados: DadosVisualizacao
    avisos: list[StrictStr] = Field(default_factory=list)

    @model_validator(mode="after")
    def validar_dados(self):
        if isinstance(self.dados, DadosBoxplot) and any(
            g.analise_id != self.metadados.analise_id for g in self.dados.grupos
        ):
            raise ValueError("Os grupos não pertencem à análise da visualização.")
        if isinstance(self.dados, DadosSerieTemporal):
            periodo = self.metadados.periodo
            if periodo is None or self.metadados.granularidade is None:
                raise ValueError("Séries exigem período e granularidade.")
            for ponto in self.dados.pontos:
                if ponto.periodo is not None and (
                    ponto.periodo.consultado.inicio != max(periodo.inicio, ponto.periodo.calendario.inicio)
                    or ponto.periodo.consultado.fim != min(periodo.fim, ponto.periodo.calendario.fim)
                ):
                    raise ValueError("O ponto não corresponde ao período consultado.")
        return self
