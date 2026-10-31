"""Consultas de OS, escopo, SQL parametrizado e normalização, sem workspace real."""

import asyncio
from datetime import date, datetime
from unittest.mock import AsyncMock

import pytest

from app.schemas.visualizacao import (
    ConsultaVisualizacaoPeriodo, ConsultaVisualizacaoSnapshot, PeriodoVisualizacao,
)
from app.services.indicadores.gerais import databricks
from app.services.visualizacoes import os_atual, os_conclusao, os_criacao


@pytest.fixture(autouse=True)
def cliente(monkeypatch):
    executar = AsyncMock(return_value=[])
    monkeypatch.setattr(databricks, "executar_consulta", executar)
    return executar


def historica(analise_id="VIS-01", filtros=None, granularidade="dia"):
    return ConsultaVisualizacaoPeriodo(
        analise_id=analise_id,
        periodo={"inicio": "2026-10-01", "fim": "2026-10-04"},
        granularidade=granularidade, filtros=filtros or {},
    )


def snapshot(analise_id="VIS-03", filtros=None):
    return ConsultaVisualizacaoSnapshot(analise_id=analise_id, filtros=filtros or {})


def consultar(servico, pedido, unidade_id=7):
    return asyncio.run(servico.consultar(pedido, unidade_id=unidade_id))


def linha_diaria(dia="2026-10-02", valor="3", quantidade="3"):
    return {"data_referencia": dia, "valor": valor, "qtd_registros": quantidade}


def linha_status():
    return {
        "status_id": "4", "status_os": "Finalizada", "valor": "2",
        "qtd_registros": "2", "instante_snapshot": "2026-10-30T12:00:00+00:00",
    }


def linha_tecnico(indice=1):
    return {
        "tecnico_id": str(indice), "tecnico_nome": f"Técnico {indice}",
        "valor": "1", "qtd_registros": "1",
        "instante_snapshot": "2026-10-30T12:00:00",
    }


CASOS = [
    (os_criacao, historica("VIS-01"), "os_criacao", "SUM(qtd_os)"),
    (os_conclusao, historica("VIS-02"), "os_conclusao", "SUM(qtd_os_finalizadas)"),
    (os_conclusao, historica("VIS-05", granularidade=None), "os_conclusao", "SUM(qtd_os_finalizadas)"),
    (os_atual, snapshot("VIS-03"), "os_atual", "COUNT(ordem_servico_id)"),
    (os_atual, snapshot("VIS-04"), "os_atual", "SUM(os_aberta)"),
    (os_atual, snapshot("VIS-22"), "os_atual", "SUM(os_prazo_vencido)"),
]


@pytest.mark.parametrize("servico,pedido,fonte,expressao", CASOS)
def test_seis_analises_usam_fonte_medida_e_unidade_obrigatorias(cliente, servico, pedido, fonte, expressao):
    resultado = consultar(servico, pedido)
    sql, parametros = cliente.await_args.args[:2]

    assert f"FROM workspace.fixa_pipeline.gold_dashboard_{fonte}" in sql
    assert f"{expressao} AS valor" in sql
    assert "WHERE unidade_id = :unidade_id" in sql
    assert parametros["unidade_id"] == 7
    assert cliente.await_args.kwargs["tipos_parametros"]["unidade_id"] == "BIGINT"
    assert set(cliente.await_args.kwargs["tipos_parametros"]) == set(parametros)
    databricks._validar_sql(sql, parametros)
    assert resultado.status == "SEM_RESULTADO"
    assert resultado.dados is None
    assert resultado.metadados.filtros_aplicados["unidade_id"] == 7
    assert resultado.metadados.qtd_registros_considerados == 0


@pytest.mark.parametrize("servico,pedido,fonte,expressao", CASOS)
def test_nenhuma_analise_consulta_sem_unidade_valida(cliente, servico, pedido, fonte, expressao):
    resultado = consultar(servico, pedido, unidade_id=0)
    assert resultado.status == "ERRO_VALIDACAO"
    assert resultado.dados is None
    cliente.assert_not_awaited()


@pytest.mark.parametrize("unidade", [None, True, False, -1, "7", 7.0])
def test_unidade_nao_e_coagida_para_inteiro(cliente, unidade):
    assert consultar(os_criacao, historica(), unidade_id=unidade).status == "ERRO_VALIDACAO"
    cliente.assert_not_awaited()


def test_series_sao_ordenadas_preenchem_lacunas_e_preservam_populacao(cliente):
    cliente.return_value = [linha_diaria("2026-10-03", "2", "2"), linha_diaria("2026-10-01", "1", "1")]
    resultado = consultar(os_criacao, historica())

    assert resultado.status == "SUCESSO"
    assert [ponto.data_referencia for ponto in resultado.dados.pontos] == [date(2026, 10, dia) for dia in (1, 2, 3)]
    assert [ponto.valor for ponto in resultado.dados.pontos] == [1, 0, 2]
    assert [ponto.qtd_registros for ponto in resultado.dados.pontos] == [1, 0, 2]
    assert resultado.metadados.qtd_registros_considerados == 3
    assert resultado.metadados.consultado_em.tzinfo is not None
    assert resultado.metadados.consulta_id


@pytest.mark.parametrize("servico,analise_id", [(os_criacao, "VIS-01"), (os_conclusao, "VIS-02")])
def test_periodo_e_inclusivo_no_inicio_e_exclusivo_no_fim(cliente, servico, analise_id):
    cliente.return_value = [linha_diaria()]
    resultado = consultar(servico, historica(analise_id))
    sql, parametros = cliente.await_args.args[:2]
    assert "data_referencia >= CAST(:inicio AS DATE)" in sql
    assert "data_referencia < CAST(:fim AS DATE)" in sql
    assert parametros["inicio"] == date(2026, 10, 1)
    assert parametros["fim"] == date(2026, 10, 4)
    assert resultado.metadados.periodo.fim == date(2026, 10, 4)
    assert len(resultado.dados.pontos) == 3


def test_tabela_de_conclusoes_vazia_nao_produz_serie_inventada_de_zeros(cliente):
    resultado = consultar(os_conclusao, historica("VIS-02"))
    assert resultado.status == "SEM_RESULTADO"
    assert resultado.dados is None
    assert resultado.metadados.fonte.endswith("gold_dashboard_os_conclusao")


def test_status_snapshot_preserva_categoria_nula_e_timestamp_da_fonte(cliente):
    linha = linha_status()
    linha.update(status_id=None, status_os=None)
    cliente.return_value = [linha]
    resultado = consultar(os_atual, snapshot())
    sql, parametros = cliente.await_args.args[:2]

    assert resultado.status == "SUCESSO"
    assert resultado.dados.pontos[0].grupo == {"status_id": None, "status_os": None}
    assert resultado.metadados.instante_snapshot == datetime.fromisoformat(linha["instante_snapshot"])
    assert resultado.metadados.periodo is None
    assert resultado.metadados.granularidade is None
    assert "MAX(data_referencia_snapshot) AS instante_snapshot" in sql
    assert "data_criacao" not in sql
    assert "inicio" not in parametros and "fim" not in parametros


def test_carga_ativa_aplica_flag_obrigatoria_e_normaliza_id_sem_perda_de_precisao(cliente):
    linha = linha_tecnico(9007199254740993)
    cliente.return_value = [linha]
    resultado = consultar(os_atual, snapshot("VIS-04"))
    sql, parametros = cliente.await_args.args[:2]
    assert "os_aberta = :obrigatorio_0" in sql
    assert parametros["obrigatorio_0"] == 1
    assert resultado.dados.pontos[0].grupo["tecnico_id"] == 9007199254740993
    assert resultado.metadados.filtros_aplicados["os_aberta"] == 1
    # Timestamp sem fuso permanece sem fuso; não presume o timezone do BI.
    assert resultado.metadados.instante_snapshot.tzinfo is None


def test_produtividade_usa_periodo_de_conclusao_e_nao_fonte_de_carga_ativa(cliente):
    linha = linha_tecnico()
    linha.pop("instante_snapshot")
    cliente.return_value = [linha]
    resultado = consultar(os_conclusao, historica("VIS-05", granularidade=None))
    sql = cliente.await_args.args[0]
    assert resultado.status == "SUCESSO"
    assert resultado.metadados.instante_snapshot is None
    assert "gold_dashboard_os_conclusao" in sql
    assert "gold_dashboard_os_atual" not in sql
    assert "SUM(qtd_os_finalizadas)" in sql


def test_prazo_vencido_por_local_preserva_zero_real_e_nao_substitui_por_atraso(cliente):
    cliente.return_value = [{
        "local_id": "12", "nome_local": None, "valor": "0", "qtd_registros": "2",
        "instante_snapshot": None,
    }]
    resultado = consultar(os_atual, snapshot("VIS-22"))
    sql, parametros = cliente.await_args.args[:2]
    assert "SUM(os_prazo_vencido)" in sql and "os_atrasada" not in sql
    assert parametros["obrigatorio_0"] == 1
    assert resultado.dados.pontos[0].valor == 0
    assert resultado.dados.pontos[0].qtd_registros == 2
    assert resultado.dados.pontos[0].grupo == {"local_id": 12, "nome_local": None}


def test_multiplos_valores_usam_in_e_campos_diferentes_usam_and(cliente):
    pedido = historica(filtros={"local_id": [10, 20], "status_id": [1, 4], "tipo_local": "Sala"})
    consultar(os_criacao, pedido)
    sql, parametros = cliente.await_args.args[:2]
    tipos = cliente.await_args.kwargs["tipos_parametros"]
    assert "local_id IN (:filtro_0_0, :filtro_0_1)" in sql
    assert "AND status_id IN (:filtro_1_0, :filtro_1_1)" in sql
    assert "AND tipo_local = :filtro_2_0" in sql
    assert parametros["filtro_0_0"] == 10 and parametros["filtro_0_1"] == 20
    assert tipos["filtro_0_0"] == "BIGINT" and tipos["filtro_1_0"] == "INT"
    assert parametros["filtro_2_0"] == "Sala" and tipos["filtro_2_0"] == "STRING"
    databricks._validar_sql(sql, parametros)


def test_texto_com_sql_continua_sendo_apenas_valor_parametrizado(cliente):
    texto = "Sala d'água' OR 1=1 --"
    consultar(os_criacao, historica(filtros={"nome_local": texto}))
    sql, parametros = cliente.await_args.args[:2]
    assert texto not in sql
    assert texto in parametros.values()
    assert "nome_local = :filtro_0_0" in sql


@pytest.mark.parametrize("filtros", [
    {"unidade_id": 9}, {"instituicao_id": 9}, {"sql": "SELECT *"},
    {"local_id": "1"}, {"status_problema": "Aprovado"}, {"local_id": list(range(51))},
])
def test_servico_direto_rejeita_filtros_invalidos_antes_de_consultar(cliente, filtros):
    resultado = consultar(os_criacao, historica(filtros=filtros))
    assert resultado.status == "ERRO_VALIDACAO"
    cliente.assert_not_awaited()


@pytest.mark.parametrize("servico,pedido", [
    (os_atual, historica("VIS-03", granularidade=None)),
    (os_criacao, snapshot("VIS-01")),
    (os_criacao, historica(granularidade=None)),
    (os_conclusao, historica("VIS-05", granularidade="mes")),
    (os_criacao, historica("VIS-15", granularidade=None)),
    (os_criacao, historica("VIS-02")),
    (os_conclusao, historica("VIS-99")),
    (os_atual, snapshot("VIS-04", filtros={"os_aberta": [0, 1]})),
])
def test_consulta_incompativel_nao_e_executada(cliente, servico, pedido):
    assert consultar(servico, pedido).status == "ERRO_VALIDACAO"
    cliente.assert_not_awaited()


def test_periodo_maior_que_366_dias_e_rejeitado_no_servico(cliente):
    pedido = historica()
    pedido.periodo = PeriodoVisualizacao(inicio="2025-01-01", fim="2026-01-03")
    resultado = consultar(os_criacao, pedido)
    assert resultado.status == "ERRO_VALIDACAO" and "366" in resultado.mensagem
    cliente.assert_not_awaited()


def test_cinquenta_categorias_sao_aceitas_e_51_nao_sao_cortadas(cliente):
    cliente.return_value = [linha_tecnico(i) for i in range(50)]
    assert len(consultar(os_atual, snapshot("VIS-04")).dados.pontos) == 50
    cliente.return_value = [linha_tecnico(i) for i in range(51)]
    resultado = consultar(os_atual, snapshot("VIS-04"))
    assert resultado.status == "ERRO_VALIDACAO" and "50" in resultado.mensagem
    assert resultado.dados is None
    assert cliente.await_args.args[0].endswith("LIMIT 51")


@pytest.mark.parametrize("erro,status", [
    (databricks.TimeoutConsultaDatabricks("segredo"), "TIMEOUT"),
    (databricks.ResultadoDatabricksTruncado("segredo"), "RESULTADO_TRUNCADO"),
    (databricks.ErroHTTPDatabricks("segredo"), "ERRO_FERRAMENTA"),
    (databricks.ConfiguracaoDatabricksAusente("segredo"), "ERRO_FERRAMENTA"),
    (RuntimeError("segredo"), "ERRO_FERRAMENTA"),
])
def test_falhas_nao_liberam_dados_nem_detalhes_de_excecao(cliente, caplog, erro, status):
    cliente.side_effect = erro
    resultado = consultar(os_criacao, historica())
    assert resultado.status == status and resultado.dados is None
    assert "segredo" not in resultado.model_dump_json()
    assert "segredo" not in caplog.text


@pytest.mark.parametrize("linhas", [
    None, [[1, 2, 3]], [{}],
    [linha_diaria(valor=None)], [linha_diaria(valor="1.5")],
    [linha_diaria(quantidade="-1")], [linha_diaria(dia="2026-10-04")],
    [linha_diaria(), linha_diaria()],
])
def test_resposta_inconsistente_nao_vira_grafico(cliente, linhas):
    cliente.return_value = linhas
    resultado = consultar(os_criacao, historica())
    assert resultado.status == "ERRO_FERRAMENTA" and resultado.dados is None


def test_rotulo_ausente_na_resposta_nao_e_inventado(cliente):
    linha = linha_tecnico()
    linha.pop("tecnico_nome")
    cliente.return_value = [linha]
    resultado = consultar(os_atual, snapshot("VIS-04"))
    assert resultado.status == "ERRO_FERRAMENTA" and resultado.dados is None


def test_categoria_repetida_no_resultado_nao_e_contada_novamente(cliente):
    cliente.return_value = [linha_status(), linha_status()]
    assert consultar(os_atual, snapshot()).status == "ERRO_FERRAMENTA"


def test_alteracao_do_pedido_durante_await_nao_muda_metadados_da_consulta(cliente):
    pedido = historica(filtros={"local_id": 10})

    async def retornar(*args, **kwargs):
        pedido.filtros["local_id"] = 999
        pedido.periodo.fim = date(2026, 10, 10)
        return [linha_diaria()]

    cliente.side_effect = retornar
    resultado = consultar(os_criacao, pedido)
    assert resultado.metadados.filtros_solicitados == {"local_id": 10}
    assert resultado.metadados.periodo.fim == date(2026, 10, 4)
    assert len(resultado.dados.pontos) == 3
    assert cliente.await_args.args[1]["filtro_0_0"] == 10
