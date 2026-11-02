"""Validação compartilhada por serviços analíticos e argumentos das tools."""


import json
from collections.abc import Mapping

from app.schemas.visualizacao import (
    Analise, ConsultaVisualizacaoPeriodo, ConsultaVisualizacaoSnapshot,
    ResultadoConsultaVisualizacao,
)
from .limites import validar_periodo_consulta, validar_limites_resultado

from app.core.respostas import MENSAGENS
from app.graph.respostas_padrao import formatar_resposta


MAXIMO_VALORES_POR_FILTRO = 50


def validar_argumentos_analise(
    consulta: ConsultaVisualizacaoPeriodo | ConsultaVisualizacaoSnapshot,
    analise: Analise,
    filtros_permitidos: Mapping[str, str],
) -> None:
    """Restringe campos e valores; não substitui a autorização do usuário."""
    if consulta.analise_id != analise.id:
        raise ValueError(MENSAGENS['a_consulta_nao_corresponde_a_analise_selecionada'])
    if analise.fonte.campo_periodo is None:
        if not isinstance(consulta, ConsultaVisualizacaoSnapshot):
            raise ValueError(MENSAGENS['a_fonte_de_snapshot_nao_aceita_periodo'])
    else:
        if not isinstance(consulta, ConsultaVisualizacaoPeriodo):
            raise ValueError(MENSAGENS['esta_analise_exige_um_periodo_explicito'])
        validar_periodo_consulta(consulta.periodo)
        if analise.formato_dados == "serie_temporal":
            if consulta.granularidade is None:
                raise ValueError(MENSAGENS['informe_a_granularidade_da_serie_temporal'])
        elif consulta.granularidade is not None:
            raise ValueError(MENSAGENS['granularidade_e_permitida_apenas_em_series_temporais'])

    obrigatorios = {filtro.campo: filtro.valor for filtro in analise.filtros_obrigatorios}
    for campo, selecao in consulta.filtros.items():
        if campo not in filtros_permitidos:
            raise ValueError(MENSAGENS['filtro_nao_permitido_para_a_fonte_desta_analise'])
        valores = selecao if isinstance(selecao, list) else [selecao]
        if not valores:
            raise ValueError(MENSAGENS['um_filtro_nao_pode_conter_uma_selecao_vazia'])
        if len(valores) > MAXIMO_VALORES_POR_FILTRO:
            raise ValueError(MENSAGENS['um_filtro_aceita_ate_50_valores_reduza_a_selecao'])
        tipo = filtros_permitidos[campo]
        for valor in valores:
            if tipo == "STRING":
                if type(valor) is not str or not valor.strip():
                    raise ValueError(MENSAGENS['este_filtro_exige_texto_nao_vazio'])
            elif tipo == "BOOLEAN":
                if type(valor) is not bool:
                    raise ValueError(formatar_resposta('o_filtro_valor_1_exige_um_booleano', valor_1=campo))
            elif tipo in {"BIGINT", "INT"}:
                if type(valor) is not int:
                    raise ValueError(MENSAGENS['este_filtro_exige_um_numero_inteiro'])
            else:
                raise ValueError(MENSAGENS['tipo_de_filtro_nao_suportado'])
            if campo in {"os_aberta", "os_atrasada", "os_prazo_vencido"} and valor not in {0, 1}:
                raise ValueError(MENSAGENS['flags_de_os_aceitam_somente_0_ou_1'])
            if campo in obrigatorios and valor != obrigatorios[campo]:
                raise ValueError(MENSAGENS['o_filtro_contradiz_a_populacao_obrigatoria_da_analise'])


def validar_resultado_consulta(
    consulta: ConsultaVisualizacaoPeriodo | ConsultaVisualizacaoSnapshot,
    analise: Analise,
    unidade_id: int,
    resultado: ResultadoConsultaVisualizacao | dict,
) -> ResultadoConsultaVisualizacao:
    """Revalida o retorno e sua correspondência com a consulta autorizada."""
    if type(unidade_id) is not int or unidade_id <= 0:
        raise ValueError(MENSAGENS['unidade_autorizada_invalida'])
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
            raise ValueError(MENSAGENS['o_resultado_nao_corresponde_a_consulta_autorizada'])
    if resultado.dados is not None:
        validar_limites_resultado(resultado.dados)
    return resultado
