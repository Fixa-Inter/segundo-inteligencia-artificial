"""Limites operacionais das análises; não corta resultados silenciosamente."""

from app.schemas.visualizacao import (
    DadosBoxplot, DadosCategorias, DadosHistograma, DadosSerieTemporal,
    DadosVisualizacao, GrupoBoxplot, PeriodoVisualizacao,
)
from .resumos import MINIMO_REGISTROS_BOXPLOT


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
        raise ValueError("O período deve ter entre 1 e 366 dias; reduza o intervalo.")


def validar_limites_resultado(dados: DadosVisualizacao) -> None:
    """Valida o resultado completo, incluindo pontos de lacunas e resumos.

    As consultas e o preenchimento das séries devem chamar esta validação antes
    de liberar seus resultados. Este validador confere os limites dos pontos
    selecionados; a consulta mantém as estatísticas da população completa.
    """
    if isinstance(dados, DadosCategorias):
        if len(dados.pontos) > MAXIMO_GRUPOS:
            raise ValueError("O gráfico excede 50 categorias; refine os filtros.")
    elif isinstance(dados, DadosSerieTemporal):
        if len(dados.pontos) > MAXIMO_PONTOS_SERIE:
            raise ValueError("A série excede 500 pontos; reduza o período ou refine os filtros.")
        grupos = {tuple(sorted(ponto.grupo.items())) for ponto in dados.pontos}
        if len(grupos) > MAXIMO_GRUPOS:
            raise ValueError("A série excede 50 grupos; refine os filtros.")
    elif isinstance(dados, DadosHistograma):
        if len(dados.intervalos) > MAXIMO_INTERVALOS_HISTOGRAMA:
            raise ValueError("O histograma excede os dez intervalos definidos.")
    elif isinstance(dados, DadosBoxplot):
        if len(dados.grupos) > MAXIMO_GRUPOS:
            raise ValueError("O gráfico excede 50 grupos; refine os filtros.")
        total_extremos = 0
        for grupo in dados.grupos:
            if isinstance(grupo, GrupoBoxplot):
                if grupo.qtd_registros < MINIMO_REGISTROS_BOXPLOT:
                    raise ValueError("Grupos com menos de cinco registros exigem resumo.")
                if len(grupo.valores_extremos) > MAXIMO_EXTREMOS_POR_GRUPO:
                    raise ValueError("O boxplot excede 50 pontos extremos enviados por grupo.")
                total_extremos += len(grupo.valores_extremos)
            elif grupo.qtd_registros >= MINIMO_REGISTROS_BOXPLOT:
                raise ValueError("Grupos com cinco ou mais registros exigem boxplot.")
        if total_extremos > MAXIMO_EXTREMOS_POR_GRAFICO:
            raise ValueError("O gráfico excede 500 pontos extremos enviados.")
    else:
        raise ValueError("Formato de resultado não suportado.")
