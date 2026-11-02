"""Captura de retornos reais das tools, isolada por execução do especialista."""


from dataclasses import dataclass, field
from uuid import uuid4

from app.schemas.visualizacao import ConsultaVisualizacaoCapturada, ReferenciaVisualizacao
from . import obter_analise, FILTROS_POR_FONTE, PERFIS_VISUALIZACOES
from .limites import MAXIMO_CONSULTAS_POR_EXECUCAO
from .validacao import validar_argumentos_analise, validar_resultado_consulta

from app.core.respostas import MENSAGENS


@dataclass(frozen=True)
class CapturaExecucaoVisualizacao:
    usuario_id: int
    sessao_id: str
    turno_id: str
    ids_anteriores: frozenset[str] = frozenset()
    execucao_id: str = field(default_factory=lambda: str(uuid4()))
    _registros: list[ConsultaVisualizacaoCapturada] = field(default_factory=list, init=False, repr=False)
    _invalida: bool = field(default=False, init=False, repr=False)

    def registrar(self, contexto, chamada_id, ferramenta, consulta, unidade_id, resultado):
        """Chamado pelo adaptador após autenticação, consulta e validação do retorno."""
        try:
            usuario = contexto.get("usuario")
            if (
                contexto.get("captura_visualizacao") is not self
                or getattr(usuario, "usuario_id", None) != self.usuario_id
                or getattr(usuario, "tipo_acesso", "").strip().lower() not in PERFIS_VISUALIZACOES
                or contexto.get("session_id") != self.sessao_id
                or contexto.get("turno_id") != self.turno_id
                or type(chamada_id) is not str or not chamada_id.strip()
                or chamada_id in self.ids_anteriores
                or len(self._registros) >= MAXIMO_CONSULTAS_POR_EXECUCAO
                or any(r.chamada_id == chamada_id for r in self._registros)
            ):
                raise ValueError(MENSAGENS['captura_incompativel_com_a_execucao_atual'])
            consulta = type(consulta).model_validate(consulta.model_dump())
            analise = obter_analise(consulta.analise_id)
            if ferramenta != f"consultar_visualizacao_{analise.fonte.id}":
                raise ValueError(MENSAGENS['ferramenta_incompativel_com_a_fonte_da_analise'])
            validar_argumentos_analise(consulta, analise, FILTROS_POR_FONTE[analise.fonte.id])
            resultado = validar_resultado_consulta(consulta, analise, unidade_id, resultado)
            if resultado.metadados is not None and any(
                r.resultado.metadados is not None
                and r.resultado.metadados.consulta_id == resultado.metadados.consulta_id
                for r in self._registros
            ):
                raise ValueError(MENSAGENS['identificador_de_consulta_repetido_nesta_execucao'])
            registro = ConsultaVisualizacaoCapturada(
                execucao_id=self.execucao_id, turno_id=self.turno_id, sessao_id=self.sessao_id,
                usuario_id=self.usuario_id, chamada_id=chamada_id, ferramenta=ferramenta,
                unidade_id=unidade_id, consulta=consulta, resultado=resultado,
            )
            # Cópia profunda: alterações posteriores no retorno da tool não mudam a captura.
            self._registros.append(ConsultaVisualizacaoCapturada.model_validate(registro.model_dump()))
        except Exception:
            object.__setattr__(self, "_invalida", True)
            raise

    def registros(self) -> list[dict]:
        return [r.model_dump(mode="json") for r in self._registros]

    def selecionar(self, referencia, status) -> dict:
        referencia = ReferenciaVisualizacao.model_validate(referencia.model_dump())
        encontrados = [r for r in self._registros if r.resultado.metadados is not None
                       and r.resultado.metadados.consulta_id == referencia.consulta_id
                       and r.resultado.metadados.analise_id == referencia.analise_id]
        if self._invalida or len(encontrados) != 1:
            raise ValueError(MENSAGENS['a_referencia_nao_identifica_uma_consulta_real_desta_execucao'])
        registro = encontrados[0]
        resultado = registro.resultado
        if resultado.status not in {"SUCESSO", "SUCESSO_PARCIAL"} or resultado.dados is None:
            raise ValueError(MENSAGENS['a_consulta_selecionada_nao_contem_dados_utilizaveis'])
        if status not in {"SUCESSO", "SUCESSO_PARCIAL"} or (
            resultado.status == "SUCESSO_PARCIAL" and status != "SUCESSO_PARCIAL"
        ):
            raise ValueError(MENSAGENS['o_status_do_especialista_oculta_uma_limitacao_da_consulta'])
        return registro.model_dump(mode="json")
