"""Intervalos e agregação completa dos histogramas aprovados."""


import math
import sys

from app.schemas.visualizacao import Analise, DadosHistograma, IntervaloHistograma
from .limites import MAXIMO_INTERVALOS_HISTOGRAMA

from app.core.respostas import MENSAGENS


def _limite_sql(indice):
    if indice == 0:
        return "minimo"
    if indice == MAXIMO_INTERVALOS_HISTOGRAMA:
        return "maximo"
    fracao = indice / MAXIMO_INTERVALOS_HISTOGRAMA
    return f"(minimo + (maximo - minimo) * CAST({fracao} AS DOUBLE))"


def montar_sql_histograma(analise: Analise, condicoes: list[str]):
    """Retorna uma linha de contagens; não limita nem transporta observações."""
    campo = analise.campo_valor
    if analise.unidade_medida == "quantidade":
        # Limites do contrato float; valores incompatíveis geram erro, sem corte.
        valido = f"{campo} >= 0 AND {campo} <= :hist_inteiro_exato AND {campo} = FLOOR({campo})"
        parametros = {"hist_inteiro_exato": 2**53}
        tipos = {"hist_inteiro_exato": "BIGINT"}
        negativo = "0"
    else:
        finito = f"NOT isnan({campo}) AND ABS({campo}) <= :hist_maximo_finito"
        valido = finito
        parametros = {"hist_maximo_finito": sys.float_info.max}
        tipos = {"hist_maximo_finito": "DOUBLE"}
        negativo = f"CASE WHEN {finito} AND {campo} < 0 THEN 1 ELSE 0 END"
    elegivel = f"{valido} AND {campo} >= 0" if analise.excluir_negativos else valido
    frequencias = []
    for indice in range(MAXIMO_INTERVALOS_HISTOGRAMA):
        inferior, superior = _limite_sql(indice), _limite_sql(indice + 1)
        if indice == 0:
            condicao = f"valor >= {inferior} AND (maximo = minimo OR valor < {superior})"
        else:
            operador = "<=" if indice == MAXIMO_INTERVALOS_HISTOGRAMA - 1 else "<"
            condicao = f"maximo > minimo AND valor >= {inferior} AND valor {operador} {superior}"
        frequencias.append(f"COUNT(CASE WHEN {condicao} THEN 1 END) AS frequencia_{indice}")
    sql = (
        "SELECT MIN(minimo) AS minimo, MAX(maximo) AS maximo,\n"
        "COUNT(*) AS qtd_registros_total, COUNT(valor) AS qtd_registros,\n"
        "COUNT(CASE WHEN negativo = 1 THEN 1 END) AS qtd_tempos_negativos_excluidos,\n"
        "COUNT(CASE WHEN inconsistente = 1 THEN 1 END) AS qtd_registros_invalidos,\n"
        f"{', '.join(frequencias)}\n"
        "FROM (\n"
        "  SELECT valor, negativo, inconsistente,\n"
        "  MIN(valor) OVER () AS minimo, MAX(valor) OVER () AS maximo\n"
        "  FROM (\n"
        f"    SELECT CASE WHEN {elegivel} THEN CAST({campo} AS DOUBLE) END AS valor,\n"
        f"    {negativo} AS negativo,\n"
        f"    CASE WHEN {campo} IS NOT NULL AND NOT ({valido}) THEN 1 ELSE 0 END AS inconsistente\n"
        f"    FROM {analise.fonte.tabela}\n"
        f"    WHERE {' AND '.join(condicoes)}\n"
        "  ) valores\n"
        ") estatisticas"
    )
    return sql, parametros, tipos


def construir_histograma(minimo, maximo, frequencias, quantidade):
    """Usa os mesmos limites do SQL, sem arredondar observações ou fronteiras."""
    if len(frequencias) != MAXIMO_INTERVALOS_HISTOGRAMA:
        raise ValueError(MENSAGENS['o_agregado_deve_conter_as_dez_frequencias_aprovadas'])
    if minimo < 0 or maximo < minimo:
        raise ValueError(MENSAGENS['limites_incompativeis_com_a_populacao_do_histograma'])
    if minimo == maximo:
        if frequencias[0] != quantidade or any(frequencias[1:]):
            raise ValueError(MENSAGENS['valores_iguais_exigem_uma_unica_frequencia'])
        intervalos = [IntervaloHistograma(
            inferior=minimo, superior=maximo, frequencia=quantidade, inclui_superior=True,
        )]
    else:
        limites = [minimo] + [
            minimo + (maximo - minimo) * (indice / MAXIMO_INTERVALOS_HISTOGRAMA)
            for indice in range(1, MAXIMO_INTERVALOS_HISTOGRAMA)
        ] + [maximo]
        if any(not math.isfinite(v) for v in limites) or any(
            inferior >= superior for inferior, superior in zip(limites, limites[1:])
        ):
            raise ValueError(MENSAGENS['a_precisao_disponivel_nao_permite_representar_dez_intervalos_distintos'])
        intervalos = [
            IntervaloHistograma(
                inferior=limites[indice], superior=limites[indice + 1],
                frequencia=frequencia,
                inclui_superior=indice == MAXIMO_INTERVALOS_HISTOGRAMA - 1,
            )
            for indice, frequencia in enumerate(frequencias)
        ]
    return DadosHistograma(intervalos=intervalos, qtd_registros=quantidade)
