"""Fronteiras dos limites aprovados e ausência de cortes silenciosos."""

from datetime import date, timedelta

import pytest

from app.schemas.visualizacao import (
    ConsultaVisualizacaoPeriodo, ConsultaVisualizacaoSnapshot,
    DadosBoxplot, DadosCategorias, DadosHistograma, DadosSerieTemporal,
    GrupoBoxplot, IntervaloHistograma, PeriodoVisualizacao, PontoCategoria,
    PontoSerieTemporal, ResumoGrupoPequeno,
)
from app.services.visualizacoes import validar_limites_resultado
from app.tools.visualizacoes import validar_consulta


def consulta(dias=366, filtros=None):
    inicio = date(2026, 1, 1)
    return ConsultaVisualizacaoPeriodo(
        analise_id="VIS-01", periodo=PeriodoVisualizacao(inicio=inicio, fim=inicio + timedelta(days=dias)),
        granularidade="dia", filtros=filtros or {},
    )


def resumo(indice=1, quantidade=1):
    return ResumoGrupoPequeno(
        analise_id="VIS-17", grupo={"tipo_local": str(indice)},
        qtd_registros=quantidade, minimo=1, maximo=1, media=1, mediana=1,
    )


def boxplot(extremos=0, indice=1, quantidade=100):
    return GrupoBoxplot(
        analise_id="VIS-17", grupo={"tipo_local": str(indice)}, qtd_registros=quantidade,
        minimo=1, q1=2, mediana=3, q3=4, maximo=100,
        limite_inferior=-1, limite_superior=7, bigode_inferior=1, bigode_superior=4,
        valores_extremos=[100] * extremos, qtd_extremos_total=extremos, qtd_extremos_omitidos=0,
    )


def test_periodo_aceita_366_dias_e_rejeita_367_sem_mudar_as_datas():
    assert validar_consulta(consulta(366), fonte_id="os_criacao").id == "VIS-01"
    dados = consulta(367)
    anterior = dados.model_dump()
    with pytest.raises(ValueError, match="366 dias"):
        validar_consulta(dados, fonte_id="os_criacao")
    assert dados.model_dump() == anterior


def test_snapshot_continua_sem_receber_periodo():
    dados = ConsultaVisualizacaoSnapshot(analise_id="VIS-03")
    assert validar_consulta(dados, fonte_id="os_atual").id == "VIS-03"


def test_filtro_aceita_50_valores_e_rejeita_51_sem_remover_selecoes():
    validar_consulta(consulta(filtros={"local_id": list(range(50))}), fonte_id="os_criacao")
    dados = consulta(filtros={"local_id": list(range(51))})
    with pytest.raises(ValueError, match="até 50 valores"):
        validar_consulta(dados, fonte_id="os_criacao")
    assert len(dados.filtros["local_id"]) == 51


def test_limite_de_filtros_e_por_campo():
    dados = consulta(filtros={"local_id": list(range(50)), "tecnico_id": list(range(50))})
    assert validar_consulta(dados, fonte_id="os_criacao").id == "VIS-01"


def test_categorias_aceitam_50_e_rejeitam_51_sem_recortar():
    pontos = [PontoCategoria(grupo={"local_id": i}, valor=1, qtd_registros=1) for i in range(51)]
    validar_limites_resultado(DadosCategorias(pontos=pontos[:50]))
    dados = DadosCategorias(pontos=pontos)
    with pytest.raises(ValueError, match="50 categorias"):
        validar_limites_resultado(dados)
    assert len(dados.pontos) == 51


def test_limite_de_series_conta_pontos_de_lacunas_sem_registros():
    inicio = date(2025, 1, 1)
    pontos = [
        PontoSerieTemporal(data_referencia=inicio + timedelta(days=i // 2), grupo={"tecnico_id": i % 2}, valor=0, qtd_registros=0)
        for i in range(501)
    ]
    validar_limites_resultado(DadosSerieTemporal(pontos=pontos[:500]))
    dados = DadosSerieTemporal(pontos=pontos)
    with pytest.raises(ValueError, match="500 pontos"):
        validar_limites_resultado(dados)
    assert len(dados.pontos) == 501


def test_limite_de_grupos_na_serie_e_independente_do_limite_de_pontos():
    dados = DadosSerieTemporal(pontos=[
        PontoSerieTemporal(data_referencia=date(2026, 1, 1), grupo={"tecnico_id": i}, valor=1, qtd_registros=1)
        for i in range(51)
    ])
    with pytest.raises(ValueError, match="50 grupos"):
        validar_limites_resultado(dados)


def test_mesmo_grupo_em_datas_distintas_nao_e_contado_como_grupos_diferentes():
    dados = DadosSerieTemporal(pontos=[
        PontoSerieTemporal(data_referencia=date(2026, 1, 1) + timedelta(days=i), grupo={"tecnico_id": None}, valor=None, qtd_registros=0)
        for i in range(100)
    ])
    validar_limites_resultado(dados)


def test_grupos_de_resumo_tambem_entram_no_limite_do_grafico():
    validar_limites_resultado(DadosBoxplot(grupos=[resumo(i) for i in range(50)]))
    dados = DadosBoxplot(grupos=[resumo(i) for i in range(51)])
    with pytest.raises(ValueError, match="50 grupos"):
        validar_limites_resultado(dados)
    assert len(dados.grupos) == 51


def test_pontos_extremos_respeitam_limites_por_grupo_e_no_total():
    validar_limites_resultado(DadosBoxplot(grupos=[boxplot(50, i) for i in range(10)]))
    with pytest.raises(ValueError, match="50 pontos extremos"):
        validar_limites_resultado(DadosBoxplot(grupos=[boxplot(51)]))
    with pytest.raises(ValueError, match="500 pontos extremos"):
        validar_limites_resultado(DadosBoxplot(grupos=[boxplot(50, i) for i in range(11)]))


def test_contagem_total_de_extremos_nao_e_limitada_aos_pontos_enviados():
    grupo = boxplot(50)
    grupo.qtd_extremos_total = 80
    grupo.qtd_extremos_omitidos = 30
    validar_limites_resultado(DadosBoxplot(grupos=[grupo]))
    assert grupo.qtd_extremos_total == 80


def test_validador_de_resultado_preserva_a_regra_de_tamanho_minimo_do_boxplot():
    with pytest.raises(ValueError, match="exigem resumo"):
        validar_limites_resultado(DadosBoxplot(grupos=[boxplot(quantidade=4)]))
    with pytest.raises(ValueError, match="exigem boxplot"):
        validar_limites_resultado(DadosBoxplot(grupos=[resumo(quantidade=5)]))


def test_histograma_nao_excede_dez_intervalos():
    intervalos = [IntervaloHistograma(inferior=i, superior=i + 1, frequencia=1, inclui_superior=False) for i in range(11)]
    validar_limites_resultado(DadosHistograma(intervalos=intervalos[:10], qtd_registros=10))
    with pytest.raises(ValueError, match="dez intervalos"):
        validar_limites_resultado(DadosHistograma(intervalos=intervalos, qtd_registros=11))
