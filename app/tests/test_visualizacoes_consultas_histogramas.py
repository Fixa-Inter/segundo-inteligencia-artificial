"""Histogramas completos, limites e populações em amostras controladas."""

import asyncio
from datetime import date
import math
import sqlite3
from unittest.mock import AsyncMock

import pytest

from app.schemas.visualizacao import ConsultaVisualizacaoPeriodo, ResultadoConsultaVisualizacao
from app.services.indicadores.gerais import databricks
from app.services.visualizacoes import os_conclusao, os_criacao, recorrencia


CASOS = [
    (os_criacao, "VIS-06", "os_criacao", "tempo_espera_minutos"),
    (os_conclusao, "VIS-07", "os_conclusao", "tempo_resolucao_minutos"),
    (recorrencia, "VIS-25", "recorrencia", "qtd_solicitacoes"),
]


@pytest.fixture(autouse=True)
def cliente(monkeypatch):
    executar = AsyncMock()
    monkeypatch.setattr(databricks, "executar_consulta", executar)
    return executar


def pedido(analise_id, *, filtros=None):
    return ConsultaVisualizacaoPeriodo(
        analise_id=analise_id, periodo={"inicio": "2026-10-01", "fim": "2026-10-04"},
        filtros=filtros or {},
    )


def consultar(servico, analise_id, *, filtros=None, unidade_id=7):
    return asyncio.run(servico.consultar(pedido(analise_id, filtros=filtros), unidade_id=unidade_id))


def executar_amostra(cliente, fonte, linhas):
    """Executa o SQL de agregação, adaptando tabela/DATE e fornecendo isnan.

    SQLite não representa NaN como o Databricks; essa semântica específica não
    é certificada por esta simulação. Infinitos são preservados pela amostra.
    """
    async def executar(sql, parametros, *, tipos_parametros):
        databricks._validar_sql(sql, parametros)
        assert set(parametros) == set(tipos_parametros)
        assert f"FROM workspace.fixa_pipeline.gold_dashboard_{fonte}" in sql
        assert "LIMIT" not in sql and "COLLECT_LIST" not in sql.upper()
        sql = sql.replace(f"workspace.fixa_pipeline.gold_dashboard_{fonte}", "amostra")
        for marcador in ("inicio", "fim"):
            sql = sql.replace(f"CAST(:{marcador} AS DATE)", f":{marcador}")
        parametros = {k: v.isoformat() if type(v) is date else v for k, v in parametros.items()}
        with sqlite3.connect(":memory:") as conexao:
            conexao.row_factory = sqlite3.Row
            conexao.create_function("isnan", 1, lambda valor: int(valor is not None and math.isnan(valor)))
            colunas = list(linhas[0])
            conexao.execute(f"CREATE TABLE amostra ({', '.join(colunas)})")
            conexao.executemany(
                f"INSERT INTO amostra VALUES ({', '.join('?' for _ in colunas)})",
                [tuple(linha[campo] for campo in colunas) for linha in linhas],
            )
            return [dict(linha) for linha in conexao.execute(sql, parametros)]
    cliente.side_effect = executar


def amostra(campo, valores):
    return [{"unidade_id": 7, "data_referencia": "2026-10-02", campo: valor} for valor in valores]


@pytest.mark.parametrize("servico,analise_id,fonte,campo", CASOS)
def test_tres_histogramas_dez_intervalos_fronteiras_sem_dupla_contagem(cliente, servico, analise_id, fonte, campo):
    executar_amostra(cliente, fonte, amostra(campo, range(11)))
    resultado = consultar(servico, analise_id)
    assert resultado.status == "SUCESSO"
    assert resultado.dados.qtd_registros == 11
    intervalos = resultado.dados.intervalos
    assert len(intervalos) == 10
    assert [i.inferior for i in intervalos] == list(range(10))
    assert [i.superior for i in intervalos] == list(range(1, 11))
    assert [i.frequencia for i in intervalos] == [1] * 9 + [2]
    assert [i.inclui_superior for i in intervalos] == [False] * 9 + [True]
    assert resultado.metadados.base_calculo.qtd_registros_total == 11
    assert resultado.metadados.qtd_registros_considerados == 11
    assert resultado.metadados.campo_valor == campo and resultado.metadados.agregacao is None
    assert resultado.metadados.fonte.endswith(f"gold_dashboard_{fonte}")
    assert ResultadoConsultaVisualizacao.model_validate_json(resultado.model_dump_json()) == resultado


@pytest.mark.parametrize("servico,analise_id,fonte,campo", CASOS)
@pytest.mark.parametrize("valor", [0, 17])
def test_valores_iguais_incluindo_zero_tem_intervalo_unico(cliente, servico, analise_id, fonte, campo, valor):
    executar_amostra(cliente, fonte, amostra(campo, [valor] * 3))
    resultado = consultar(servico, analise_id)
    assert resultado.status == "SUCESSO" and len(resultado.dados.intervalos) == 1
    intervalo = resultado.dados.intervalos[0]
    assert intervalo.inferior == intervalo.superior == valor
    assert intervalo.frequencia == 3 and intervalo.inclui_superior


@pytest.mark.parametrize("servico,analise_id,fonte,campo", CASOS)
def test_intervalos_vazios_recebem_frequencia_zero(cliente, servico, analise_id, fonte, campo):
    executar_amostra(cliente, fonte, amostra(campo, [0, 100]))
    resultado = consultar(servico, analise_id)
    assert [i.frequencia for i in resultado.dados.intervalos] == [1] + [0] * 8 + [1]


@pytest.mark.parametrize("servico,analise_id,fonte,campo", CASOS)
def test_fonte_sem_linhas_no_recorte_e_diferente_de_observacoes_nulas(cliente, servico, analise_id, fonte, campo):
    fora = amostra(campo, [10])
    fora[0]["unidade_id"] = 8
    executar_amostra(cliente, fonte, fora)
    vazio = consultar(servico, analise_id)
    assert vazio.status == "SEM_RESULTADO" and vazio.dados is None
    assert vazio.metadados.base_calculo.qtd_registros_total == 0
    executar_amostra(cliente, fonte, amostra(campo, [None, None]))
    sem_base = consultar(servico, analise_id)
    assert sem_base.status == "SEM_BASE_CALCULO" and sem_base.dados is None
    assert sem_base.metadados.base_calculo.qtd_registros_total == 2
    assert sem_base.metadados.qtd_registros_considerados == 0


@pytest.mark.parametrize("servico,analise_id,fonte,campo", CASOS[:2])
def test_tempos_negativos_excluidos_sao_contados_e_nulos_nao_viram_zero(cliente, servico, analise_id, fonte, campo):
    executar_amostra(cliente, fonte, amostra(campo, [-7, -1, None, 0, 10]))
    resultado = consultar(servico, analise_id)
    assert resultado.status == "SUCESSO_PARCIAL"
    assert resultado.dados.qtd_registros == 2
    assert resultado.dados.intervalos[0].inferior == 0
    assert sum(i.frequencia for i in resultado.dados.intervalos) == 2
    assert resultado.metadados.base_calculo.qtd_registros_total == 5
    assert resultado.metadados.base_calculo.qtd_tempos_negativos_excluidos == 2
    assert any("negativos excluídos: 2" in aviso for aviso in resultado.avisos)
    assert all("média" not in aviso for aviso in resultado.avisos)


@pytest.mark.parametrize("servico,analise_id,fonte,campo", CASOS[:2])
def test_so_tempos_negativos_nao_fabricam_intervalo_zero(cliente, servico, analise_id, fonte, campo):
    executar_amostra(cliente, fonte, amostra(campo, [-7, -1]))
    resultado = consultar(servico, analise_id)
    assert resultado.status == "SEM_BASE_CALCULO" and resultado.dados is None
    assert resultado.metadados.base_calculo.qtd_tempos_negativos_excluidos == 2


@pytest.mark.parametrize("servico,analise_id,fonte,campo", CASOS)
def test_populacao_maior_que_transporte_e_contada_por_inteiro(cliente, servico, analise_id, fonte, campo):
    executar_amostra(cliente, fonte, amostra(campo, list(range(11)) * 200))
    resultado = consultar(servico, analise_id)
    assert resultado.status == "SUCESSO" and resultado.dados.qtd_registros == 2200
    assert [i.frequencia for i in resultado.dados.intervalos] == [200] * 9 + [400]


def test_filtros_unidade_e_periodo_sao_aplicados_antes_da_faixa(cliente):
    linhas = []
    for unidade, dia, local, valor in [
        (7, "2026-10-01", "001", 0), (7, "2026-10-03", "001", 10),
        (8, "2026-10-02", "001", 1000), (7, "2026-10-04", "001", 1000),
        (7, "2026-09-30", "001", 1000), (7, "2026-10-02", "1", 1000),
    ]:
        linhas.append({"unidade_id": unidade, "data_referencia": dia, "local_id": local,
                       "qtd_solicitacoes": valor})
    executar_amostra(cliente, "recorrencia", linhas)
    resultado = consultar(recorrencia, "VIS-25", filtros={"local_id": ["001", "002"]})
    assert resultado.dados.qtd_registros == 2 and resultado.dados.intervalos[-1].superior == 10
    sql, parametros = cliente.await_args.args
    assert "local_id IN (:filtro_0_0, :filtro_0_1)" in sql
    assert parametros["filtro_0_0"] == "001"
    assert cliente.await_args.kwargs["tipos_parametros"]["filtro_0_0"] == "STRING"


def test_limites_decimais_contam_vizinhos_e_fronteiras_com_os_mesmos_numeros(cliente):
    limites = [0.1] + [0.1 + (1.1 - 0.1) * (i / 10) for i in range(1, 10)] + [1.1]
    valores = limites + [math.nextafter(limites[3], -math.inf), math.nextafter(limites[3], math.inf)]
    executar_amostra(cliente, "os_criacao", amostra("tempo_espera_minutos", valores))
    resultado = consultar(os_criacao, "VIS-06")
    assert resultado.status == "SUCESSO"
    assert [i.inferior for i in resultado.dados.intervalos] == limites[:-1]
    assert [i.frequencia for i in resultado.dados.intervalos] == [1, 1, 2, 2, 1, 1, 1, 1, 1, 2]


@pytest.mark.parametrize("invalido", [float("inf"), -float("inf")])
def test_valores_nao_finitos_nao_sao_excluidos_silenciosamente_como_negativos(cliente, invalido):
    executar_amostra(cliente, "os_criacao", amostra("tempo_espera_minutos", [0, invalido, 10]))
    resultado = consultar(os_criacao, "VIS-06")
    assert resultado.status == "ERRO_FERRAMENTA" and resultado.dados is None


@pytest.mark.parametrize("invalido", [-1, 1.5, 2**53 + 1])
def test_quantidade_invalida_ou_nao_representavel_nao_recebe_intervalo_impreciso(cliente, invalido):
    executar_amostra(cliente, "recorrencia", amostra("qtd_solicitacoes", [1, invalido]))
    assert consultar(recorrencia, "VIS-25").status == "ERRO_FERRAMENTA"


def test_faixa_com_precisao_insuficiente_para_dez_intervalos_nao_e_deformada(cliente):
    executar_amostra(cliente, "os_criacao", amostra("tempo_espera_minutos", [1, math.nextafter(1, math.inf)]))
    assert consultar(os_criacao, "VIS-06").status == "ERRO_FERRAMENTA"


def resposta():
    return {
        "minimo": "0", "maximo": "10", "qtd_registros_total": "2", "qtd_registros": "2",
        "qtd_tempos_negativos_excluidos": "0", "qtd_registros_invalidos": "0",
        **{f"frequencia_{i}": "1" if i in {0, 9} else "0" for i in range(10)},
    }


@pytest.mark.parametrize("alteracao", [
    {"qtd_registros_invalidos": "1"}, {"frequencia_9": "0"}, {"frequencia_0": "-1"},
    {"qtd_registros": "3"}, {"qtd_tempos_negativos_excluidos": "1"},
    {"minimo": "NaN"}, {"maximo": "Infinity"}, {"maximo": "-1"}, {"minimo": True},
    {"qtd_registros_total": "1.5"}, {"frequencia_0": False},
    {"minimo": "10", "frequencia_0": "1", "frequencia_9": "1"},
    {"minimo": None, "maximo": None},
])
def test_resposta_incompativel_nao_libera_histograma(cliente, alteracao):
    cliente.return_value = [{**resposta(), **alteracao}]
    assert consultar(os_criacao, "VIS-06").status == "ERRO_FERRAMENTA"


@pytest.mark.parametrize("campo", ["frequencia_5", "qtd_registros_total", "qtd_registros_invalidos", "minimo"])
def test_colunas_ausentes_nao_sao_preenchidas_com_zero(cliente, campo):
    linha = resposta()
    linha.pop(campo)
    cliente.return_value = [linha]
    assert consultar(os_criacao, "VIS-06").status == "ERRO_FERRAMENTA"


@pytest.mark.parametrize("linhas", [[], [resposta(), resposta()]])
def test_agregado_deve_ter_uma_linha(cliente, linhas):
    cliente.return_value = linhas
    assert consultar(os_criacao, "VIS-06").status == "ERRO_FERRAMENTA"


@pytest.mark.parametrize("servico,analise_id,fonte,campo", CASOS)
def test_unidade_invalida_impede_acesso_ao_histograma(cliente, servico, analise_id, fonte, campo):
    assert consultar(servico, analise_id, unidade_id=0).status == "ERRO_VALIDACAO"
    cliente.assert_not_awaited()


@pytest.mark.parametrize("filtros", [{"unidade_id": 8}, {"sql": "SELECT 1"}, {"intervalos": 20}, {"status_problema_id": 1}])
def test_histograma_nao_aceita_escopo_fonte_ou_numero_de_intervalos_livres(cliente, filtros):
    assert consultar(recorrencia, "VIS-25", filtros=filtros).status == "ERRO_VALIDACAO"
    cliente.assert_not_awaited()


@pytest.mark.parametrize("erro,status", [
    (databricks.TimeoutConsultaDatabricks("segredo"), "TIMEOUT"),
    (databricks.ResultadoDatabricksTruncado("segredo"), "RESULTADO_TRUNCADO"),
    (RuntimeError("segredo"), "ERRO_FERRAMENTA"),
])
def test_falhas_nao_liberam_distribuicao_parcial_ou_detalhes_internos(cliente, erro, status):
    cliente.side_effect = erro
    resultado = consultar(os_criacao, "VIS-06")
    assert resultado.status == status and resultado.dados is None
    assert "segredo" not in resultado.model_dump_json()
