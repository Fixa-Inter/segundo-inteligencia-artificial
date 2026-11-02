"""Limites operacionais das análises; não corta resultados silenciosamente."""


from app.schemas.visualizacao import (
    DadosBoxplot, DadosCategorias, DadosHistograma, DadosSerieTemporal,
    DadosVisualizacao, GrupoBoxplot, PeriodoVisualizacao,
)
from .resumos import MINIMO_REGISTROS_BOXPLOT

from app.core.respostas import MENSAGENS


MAXIMO_DIAS_PERIODO = 366
MAXIMO_GRUPOS = 50
MAXIMO_PONTOS_SERIE = 500
MAXIMO_INTERVALOS_HISTOGRAMA = 10
MAXIMO_EXTREMOS_POR_GRUPO = 50
MAXIMO_EXTREMOS_POR_GRAFICO = 500
MAXIMO_CONSULTAS_POR_EXECUCAO = 3


def validar_periodo_consulta(periodo: PeriodoVisualizacao) -> None:
    dias = (periodo.fim - periodo.inicio).days
    if not 1 <= dias <= MAXIMO_DIAS_PERIODO:
        raise ValueError(MENSAGENS['o_periodo_deve_ter_entre_1_e_366_dias_reduza_o_intervalo'])


def validar_limites_resultado(dados: DadosVisualizacao) -> None:
    """Valida o resultado completo, incluindo pontos de lacunas e resumos.

    As consultas e o preenchimento das séries devem chamar esta validação antes
    de liberar seus resultados. Este validador confere os limites dos pontos
    selecionados; a consulta mantém as estatísticas da população completa.
    """
    if isinstance(dados, DadosCategorias):
        if len(dados.pontos) > MAXIMO_GRUPOS:
            raise ValueError(MENSAGENS['o_grafico_excede_50_categorias_refine_os_filtros'])
    elif isinstance(dados, DadosSerieTemporal):
        if len(dados.pontos) > MAXIMO_PONTOS_SERIE:
            raise ValueError(MENSAGENS['a_serie_excede_500_pontos_reduza_o_periodo_ou_refine_os_filtros'])
        grupos = {tuple(sorted(ponto.grupo.items())) for ponto in dados.pontos}
        if len(grupos) > MAXIMO_GRUPOS:
            raise ValueError(MENSAGENS['a_serie_excede_50_grupos_refine_os_filtros'])
    elif isinstance(dados, DadosHistograma):
        if len(dados.intervalos) > MAXIMO_INTERVALOS_HISTOGRAMA:
            raise ValueError(MENSAGENS['o_histograma_excede_os_dez_intervalos_definidos'])
    elif isinstance(dados, DadosBoxplot):
        if len(dados.grupos) > MAXIMO_GRUPOS:
            raise ValueError(MENSAGENS['o_grafico_excede_50_grupos_refine_os_filtros'])
        total_extremos = 0
        for grupo in dados.grupos:
            if isinstance(grupo, GrupoBoxplot):
                if grupo.qtd_registros < MINIMO_REGISTROS_BOXPLOT:
                    raise ValueError(MENSAGENS['grupos_com_menos_de_cinco_registros_exigem_resumo'])
                if len(grupo.valores_extremos) > MAXIMO_EXTREMOS_POR_GRUPO:
                    raise ValueError(MENSAGENS['o_boxplot_excede_50_pontos_extremos_enviados_por_grupo'])
                total_extremos += len(grupo.valores_extremos)
            elif grupo.qtd_registros >= MINIMO_REGISTROS_BOXPLOT:
                raise ValueError(MENSAGENS['grupos_com_cinco_ou_mais_registros_exigem_boxplot'])
        if total_extremos > MAXIMO_EXTREMOS_POR_GRAFICO:
            raise ValueError(MENSAGENS['o_grafico_excede_500_pontos_extremos_enviados'])
    else:
        raise ValueError(MENSAGENS['formato_de_resultado_nao_suportado'])
