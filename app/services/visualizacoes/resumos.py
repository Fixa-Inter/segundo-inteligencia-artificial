"""Resumo dos grupos pequenos das análises de boxplot, sem acesso a bancos."""


from collections.abc import Mapping, Sequence
from math import isfinite
from statistics import fmean, median

from app.schemas.visualizacao import Analise, ResumoGrupoPequeno

from app.core.respostas import MENSAGENS


MINIMO_REGISTROS_BOXPLOT = 5


def resumir_grupo_pequeno(
    analise: Analise,
    *,
    grupo: Mapping[str, int | str | None],
    valores: Sequence[int | float | None],
) -> ResumoGrupoPequeno | None:
    """Resume até quatro tempos não nulos; sem observações, não fabrica resumo.

    Recebe a população do grupo já selecionada e autorizada pelo chamador. Não
    autentica, não consulta bancos e não trunca grupos para caber no resumo.
    A normalização dos tipos retornados pelo Databricks precede esta função.
    A elegibilidade além dos nulos, inclusive de tempos negativos, cabe ao chamador.
    """
    if analise.formato_dados != "boxplot" or analise.unidade_medida != "minutos":
        raise ValueError(MENSAGENS['o_resumo_se_aplica_as_analises_de_boxplot_de_tempos'])
    if set(grupo) != set(analise.dimensoes):
        raise ValueError(MENSAGENS['as_dimensoes_do_grupo_nao_correspondem_a_analise'])

    observacoes = []
    for valor in valores:
        if valor is None:
            continue
        if type(valor) not in {int, float}:
            raise ValueError(MENSAGENS['os_tempos_devem_ser_numeros_normalizados_ou_nulos'])
        try:
            numero = float(valor)
        except OverflowError as erro:
            raise ValueError(MENSAGENS['os_tempos_devem_ser_numeros_finitos']) from erro
        if not isfinite(numero):
            raise ValueError(MENSAGENS['os_tempos_devem_ser_numeros_finitos'])
        observacoes.append(numero)

    if not observacoes:
        return None
    if len(observacoes) >= MINIMO_REGISTROS_BOXPLOT:
        raise ValueError(MENSAGENS['grupos_com_cinco_ou_mais_registros_devem_usar_boxplot'])

    return ResumoGrupoPequeno(
        analise_id=analise.id,
        grupo=dict(grupo),
        qtd_registros=len(observacoes),
        minimo=min(observacoes),
        maximo=max(observacoes),
        media=fmean(observacoes),
        mediana=median(observacoes),
    )
