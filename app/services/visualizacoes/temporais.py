"""Calendários e expressões SQL das granularidades temporais aprovadas."""


from datetime import date, timedelta

from app.schemas.visualizacao import PeriodoSerieTemporal, PeriodoVisualizacao

from app.core.respostas import MENSAGENS


def inicio_periodo(referencia: date, granularidade: str) -> date:
    if granularidade == "dia":
        return referencia
    if granularidade == "semana":
        return referencia - timedelta(days=referencia.weekday())
    if granularidade == "mes":
        return referencia.replace(day=1)
    raise ValueError(MENSAGENS['granularidade_temporal_nao_suportada'])


def proximo_periodo(referencia: date, granularidade: str) -> date:
    try:
        if granularidade == "dia":
            return referencia + timedelta(days=1)
        if granularidade == "semana":
            return referencia + timedelta(days=7)
        if granularidade == "mes":
            if referencia.month == 12:
                return referencia.replace(year=referencia.year + 1, month=1, day=1)
            return referencia.replace(month=referencia.month + 1, day=1)
    except (OverflowError, ValueError) as erro:
        raise ValueError(MENSAGENS['o_calendario_solicitado_excede_as_datas_representaveis']) from erro
    raise ValueError(MENSAGENS['granularidade_temporal_nao_suportada'])


def expressao_periodo_sql(campo: str, granularidade: str) -> str:
    """Campo canônico do serviço; unidade SQL selecionada de uma lista fechada."""
    if granularidade == "dia":
        return campo
    unidades = {"semana": "WEEK", "mes": "MONTH"}
    if granularidade not in unidades:
        raise ValueError(MENSAGENS['granularidade_temporal_nao_suportada'])
    return f"TRUNC({campo}, '{unidades[granularidade]}')"


def calendario_consulta(periodo: PeriodoVisualizacao, granularidade: str) -> dict[date, PeriodoSerieTemporal]:
    """Preserva o recorte solicitado, inclusive nas extremidades incompletas."""
    calendario = {}
    referencia = inicio_periodo(periodo.inicio, granularidade)
    while referencia < periodo.fim:
        seguinte = proximo_periodo(referencia, granularidade)
        intervalo = PeriodoVisualizacao(inicio=referencia, fim=seguinte)
        consultado = PeriodoVisualizacao(
            inicio=max(referencia, periodo.inicio), fim=min(seguinte, periodo.fim),
        )
        calendario[referencia] = PeriodoSerieTemporal(
            calendario=intervalo, consultado=consultado, parcial=intervalo != consultado,
        )
        referencia = seguinte
    return calendario
