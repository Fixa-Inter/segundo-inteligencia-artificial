"""Validação compartilhada por serviços analíticos e argumentos das tools."""

import json
from collections.abc import Mapping

from app.schemas.visualizacao import (
    Analise, ConsultaVisualizacaoPeriodo, ConsultaVisualizacaoSnapshot,
    ResultadoConsultaVisualizacao,
)
from .limites import validar_periodo_consulta, validar_limites_resultado


MAXIMO_VALORES_POR_FILTRO = 50


def validar_argumentos_analise(
    consulta: ConsultaVisualizacaoPeriodo | ConsultaVisualizacaoSnapshot,
    analise: Analise,
    filtros_permitidos: Mapping[str, str],
) -> None:
    """Restringe campos e valores; não substitui a autorização do usuário."""
    if consulta.analise_id != analise.id:
        raise ValueError("A consulta não corresponde à análise selecionada.")
    if analise.fonte.campo_periodo is None:
        if not isinstance(consulta, ConsultaVisualizacaoSnapshot):
            raise ValueError("A fonte de snapshot não aceita período.")
    else:
        if not isinstance(consulta, ConsultaVisualizacaoPeriodo):
            raise ValueError("Esta análise exige um período explícito.")
        validar_periodo_consulta(consulta.periodo)
        if analise.formato_dados == "serie_temporal":
            if consulta.granularidade is None:
                raise ValueError("Informe a granularidade da série temporal.")
        elif consulta.granularidade is not None:
            raise ValueError("Granularidade é permitida apenas em séries temporais.")

    obrigatorios = {filtro.campo: filtro.valor for filtro in analise.filtros_obrigatorios}
    for campo, selecao in consulta.filtros.items():
        if campo not in filtros_permitidos:
            raise ValueError("Filtro não permitido para a fonte desta análise.")
        valores = selecao if isinstance(selecao, list) else [selecao]
        if not valores:
            raise ValueError("Um filtro não pode conter uma seleção vazia.")
        if len(valores) > MAXIMO_VALORES_POR_FILTRO:
            raise ValueError("Um filtro aceita até 50 valores; reduza a seleção.")
        tipo = filtros_permitidos[campo]
        for valor in valores:
            if tipo == "STRING":
                if type(valor) is not str or not valor.strip():
                    raise ValueError("Este filtro exige texto não vazio.")
            elif tipo == "BOOLEAN":
                if type(valor) is not bool:
                    raise ValueError(f"O filtro {campo} exige um booleano.")
            elif tipo in {"BIGINT", "INT"}:
                if type(valor) is not int:
                    raise ValueError("Este filtro exige um número inteiro.")
            else:
                raise ValueError("Tipo de filtro não suportado.")
            if campo in {"os_aberta", "os_atrasada", "os_prazo_vencido"} and valor not in {0, 1}:
                raise ValueError("Flags de OS aceitam somente 0 ou 1.")
            if campo in obrigatorios and valor != obrigatorios[campo]:
                raise ValueError("O filtro contradiz a população obrigatória da análise.")


def validar_resultado_consulta(
    consulta: ConsultaVisualizacaoPeriodo | ConsultaVisualizacaoSnapshot,
    analise: Analise,
    unidade_id: int,
    resultado: ResultadoConsultaVisualizacao | dict,
) -> ResultadoConsultaVisualizacao:
    """Revalida o retorno e sua correspondência com a consulta autorizada."""
    if type(unidade_id) is not int or unidade_id <= 0:
        raise ValueError("Unidade autorizada inválida.")
    if isinstance(resultado, ResultadoConsultaVisualizacao):
        resultado = resultado.model_dump()
    resultado = ResultadoConsultaVisualizacao.model_validate(resultado)
    metadados = resultado.metadados
    if metadados is not None:
        aplicados = {**consulta.filtros, "unidade_id": unidade_id}
        aplicados.update({f.campo: f.valor for f in analise.filtros_obrigatorios})
        # Comparação JSON distingue bool/int e mantém os tipos dos filtros.
        if (
            metadados.analise_id != consulta.analise_id
            or metadados.fonte != analise.fonte.tabela
            or metadados.periodo != getattr(consulta, "periodo", None)
            or metadados.granularidade != getattr(consulta, "granularidade", None)
            or json.dumps(metadados.filtros_solicitados, sort_keys=True) != json.dumps(consulta.filtros, sort_keys=True)
            or json.dumps(metadados.filtros_aplicados, sort_keys=True) != json.dumps(aplicados, sort_keys=True)
            or metadados.filtros_nao_aplicados
            or type(metadados.filtros_aplicados.get("unidade_id")) is not int
            or any(getattr(metadados, c) != getattr(analise, c) for c in (
                "formato_dados", "campo_valor", "agregacao", "unidade_medida", "escala_percentual",
            ))
        ):
            raise ValueError("O resultado não corresponde à consulta autorizada.")
    if resultado.dados is not None:
        validar_limites_resultado(resultado.dados)
    return resultado
