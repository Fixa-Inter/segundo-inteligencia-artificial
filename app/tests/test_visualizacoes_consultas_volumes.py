"""Volumes de solicitações, episódios e ocorrências com Databricks simulado."""

import asyncio
from datetime import date, timedelta
from unittest.mock import AsyncMock

import pytest

from app.schemas.visualizacao import ConsultaVisualizacaoPeriodo, ConsultaVisualizacaoSnapshot
from app.services.indicadores.gerais import databricks
from app.services.visualizacoes import ocorrencia, recorrencia, solicitacao


@pytest.fixture(autouse=True)
def cliente(monkeypatch):
    executar = AsyncMock(return_value=[])
    monkeypatch.setattr(databricks, "executar_consulta", executar)
    return executar


def pedido(analise_id, *, filtros=None, dias=3, inicio=date(2026, 10, 1)):
    return ConsultaVisualizacaoPeriodo(
        analise_id=analise_id,
        periodo={"inicio": inicio, "fim": inicio + timedelta(days=dias)},
        granularidade="dia" if analise_id in {"VIS-09", "VIS-26"} else None,
        filtros=filtros or {},
    )


def consultar(servico, consulta, unidade_id=7):
    return asyncio.run(servico.consultar(consulta, unidade_id=unidade_id))


def prioridade(codigo, nome, dia="2026-10-02", valor="1", quantidade="1"):
    return {
        "data_referencia": dia, "prioridade": codigo, "prioridade_nome": nome,
        "valor": valor, "qtd_registros": quantidade,
    }


CASOS = [
    (solicitacao, "VIS-08", "solicitacao", "qtd_solicitacoes", ("status_problema_id", "status_problema"),
     {"status_problema_id": "1", "status_problema": "Aprovado", "valor": "3", "qtd_registros": "3"}),
    (solicitacao, "VIS-09", "solicitacao", "qtd_solicitacoes", ("data_referencia",),
     {"data_referencia": "2026-10-02", "valor": "3", "qtd_registros": "3"}),
    (solicitacao, "VIS-10", "solicitacao", "qtd_solicitacoes", ("local_id", "nome_local"),
     {"local_id": "3", "nome_local": "Laboratório", "valor": "3", "qtd_registros": "3"}),
    (solicitacao, "VIS-11", "solicitacao", "qtd_solicitacoes", ("categoria_equipamento_id", "categoria_equipamento"),
     {"categoria_equipamento_id": "7", "categoria_equipamento": "Ar", "valor": "3", "qtd_registros": "3"}),
    (recorrencia, "VIS-12", "recorrencia", "qtd_episodios_recorrentes", ("categoria_equipamento_id", "categoria_equipamento"),
     {"categoria_equipamento_id": "007", "categoria_equipamento": "Ar", "valor": "2", "qtd_registros": "5"}),
    (recorrencia, "VIS-13", "recorrencia", "qtd_episodios_recorrentes", ("local_id", "nome_local"),
     {"local_id": "003", "nome_local": "Laboratório", "valor": "2", "qtd_registros": "5"}),
    (ocorrencia, "VIS-26", "ocorrencia", "qtd_ocorrencias", ("data_referencia", "prioridade", "prioridade_nome"),
     prioridade("0", "Alta")),
    (ocorrencia, "VIS-27", "ocorrencia", "ocorrencia_alta_prioridade", ("local_id", "nome_local"),
     {"local_id": "3", "nome_local": "Laboratório", "valor": "2", "qtd_registros": "5"}),
]


@pytest.mark.parametrize("servico,analise_id,fonte,medida,dimensoes,linha", CASOS)
def test_oito_consultas_usam_fonte_medida_agrupamento_e_escopo_corretos(cliente, servico, analise_id, fonte, medida, dimensoes, linha):
    cliente.return_value = [linha]
    resultado = consultar(servico, pedido(analise_id))
    sql, parametros = cliente.await_args.args[:2]

    assert resultado.status == "SUCESSO"
    assert f"FROM workspace.fixa_pipeline.gold_dashboard_{fonte}" in sql
    assert f"SUM({medida}) AS valor" in sql
    assert f"GROUP BY {', '.join(dimensoes)}" in sql
    assert "WHERE unidade_id = :unidade_id" in sql
    assert "data_referencia >= CAST(:inicio AS DATE)" in sql
    assert "data_referencia < CAST(:fim AS DATE)" in sql
    assert parametros["unidade_id"] == 7
    assert parametros["inicio"] == date(2026, 10, 1)
    assert parametros["fim"] == date(2026, 10, 4)
    assert set(cliente.await_args.kwargs["tipos_parametros"]) == set(parametros)
    databricks._validar_sql(sql, parametros)
    assert resultado.metadados.campo_valor == medida
    assert resultado.metadados.fonte.endswith(f"gold_dashboard_{fonte}")
    assert resultado.metadados.qtd_registros_considerados == int(linha["qtd_registros"])
    assert resultado.metadados.filtros_aplicados["unidade_id"] == 7


@pytest.mark.parametrize("servico,analise_id,fonte,medida,dimensoes,linha", CASOS)
def test_nenhuma_consulta_executa_sem_unidade(cliente, servico, analise_id, fonte, medida, dimensoes, linha):
    assert consultar(servico, pedido(analise_id), unidade_id=0).status == "ERRO_VALIDACAO"
    cliente.assert_not_awaited()


@pytest.mark.parametrize("servico,analise_id,fonte,medida,dimensoes,linha", CASOS)
def test_fonte_vazia_nao_cria_categorias_nem_calendario_de_zeros(cliente, servico, analise_id, fonte, medida, dimensoes, linha):
    resultado = consultar(servico, pedido(analise_id))
    assert resultado.status == "SEM_RESULTADO"
    assert resultado.dados is None
    assert resultado.metadados.qtd_registros_considerados == 0


def test_solicitacoes_por_dia_preenchem_lacunas_sem_aumentar_populacao(cliente):
    cliente.return_value = [{"data_referencia": "2026-10-02", "valor": "4", "qtd_registros": "4"}]
    resultado = consultar(solicitacao, pedido("VIS-09"))
    assert [ponto.valor for ponto in resultado.dados.pontos] == [0, 4, 0]
    assert [ponto.qtd_registros for ponto in resultado.dados.pontos] == [0, 4, 0]
    assert resultado.metadados.qtd_registros_considerados == 4


def test_status_de_solicitacao_e_aplicado_somente_na_fonte_correta(cliente):
    consultar(solicitacao, pedido("VIS-10", filtros={"status_problema": ["Aprovado", "Pendente"]}))
    sql, parametros = cliente.await_args.args[:2]
    assert "status_problema IN (:filtro_0_0, :filtro_0_1)" in sql
    assert parametros["filtro_0_0"] == "Aprovado"
    cliente.reset_mock()
    resultado = consultar(recorrencia, pedido("VIS-13", filtros={"status_problema": "Aprovado"}))
    assert resultado.status == "ERRO_VALIDACAO"
    cliente.assert_not_awaited()


def test_recorrencia_preserva_ids_textuais_zeros_a_esquerda_e_locais_homonimos(cliente):
    cliente.return_value = [
        {"local_id": "001", "nome_local": "Laboratório", "valor": "1", "qtd_registros": "2"},
        {"local_id": "1", "nome_local": "Laboratório", "valor": "2", "qtd_registros": "3"},
    ]
    resultado = consultar(recorrencia, pedido("VIS-13", filtros={"local_id": ["001", "1"]}))
    assert [ponto.grupo["local_id"] for ponto in resultado.dados.pontos] == ["001", "1"]
    assert [ponto.valor for ponto in resultado.dados.pontos] == [1, 2]
    assert resultado.metadados.qtd_registros_considerados == 5
    sql, parametros = cliente.await_args.args[:2]
    tipos = cliente.await_args.kwargs["tipos_parametros"]
    assert parametros["filtro_0_0"] == "001" and tipos["filtro_0_0"] == "STRING"
    assert "SUM(qtd_solicitacoes)" not in sql
    assert "inicio_episodio" not in sql
    assert "CAST(local_id" not in sql


def test_prioridades_preenchem_cada_grupo_e_mantem_ordem_com_dimensoes_nulas(cliente):
    cliente.return_value = [
        prioridade("2", "Baixa", "2026-10-03", "2", "2"),
        prioridade(None, None, "2026-10-02", "3", "3"),
        prioridade("0", "Alta", "2026-10-01", "1", "1"),
    ]
    resultado = consultar(ocorrencia, pedido("VIS-26"))
    pontos = resultado.dados.pontos
    assert resultado.status == "SUCESSO" and len(pontos) == 9
    assert [ponto.data_referencia for ponto in pontos] == [date(2026, 10, dia) for dia in (1, 1, 1, 2, 2, 2, 3, 3, 3)]
    assert [ponto.grupo["prioridade"] for ponto in pontos] == [None, 0, 2] * 3
    assert [ponto.valor for ponto in pontos] == [0, 1, 0, 3, 0, 0, 0, 0, 2]
    assert pontos[0].grupo["prioridade_nome"] is None
    assert resultado.metadados.qtd_registros_considerados == 6


def test_nao_inventa_grupo_para_prioridade_sem_registros_no_periodo(cliente):
    cliente.return_value = [prioridade("0", "Alta")]
    resultado = consultar(ocorrencia, pedido("VIS-26", filtros={"prioridade": [0, 1]}))
    assert len(resultado.dados.pontos) == 3
    assert all(ponto.grupo == {"prioridade": 0, "prioridade_nome": "Alta"} for ponto in resultado.dados.pontos)


def test_prioridade_com_nome_nulo_nao_ganha_rotulo_inferido(cliente):
    cliente.return_value = [prioridade("0", None)]
    resultado = consultar(ocorrencia, pedido("VIS-26"))
    assert all(ponto.grupo["prioridade_nome"] is None for ponto in resultado.dados.pontos)


def test_limite_de_500_pontos_e_global_e_inclui_lacunas_de_todos_os_grupos(cliente):
    inicio = date(2026, 1, 1)
    cliente.return_value = [prioridade("0", "Alta", inicio.isoformat()), prioridade("1", "Média", inicio.isoformat())]
    resultado = consultar(ocorrencia, pedido("VIS-26", inicio=inicio, dias=250))
    assert resultado.status == "SUCESSO" and len(resultado.dados.pontos) == 500
    resultado = consultar(ocorrencia, pedido("VIS-26", inicio=inicio, dias=251))
    assert resultado.status == "ERRO_VALIDACAO" and "500" in resultado.mensagem
    assert resultado.dados is None


def test_serie_aceita_50_grupos_e_rejeita_51_sem_cortar(cliente):
    cliente.return_value = [prioridade(str(i), f"Prioridade {i}", "2026-10-01") for i in range(50)]
    resultado = consultar(ocorrencia, pedido("VIS-26", dias=1))
    assert resultado.status == "SUCESSO" and len(resultado.dados.pontos) == 50
    cliente.return_value.append(prioridade("50", "Prioridade 50", "2026-10-01"))
    resultado = consultar(ocorrencia, pedido("VIS-26", dias=1))
    assert resultado.status == "ERRO_VALIDACAO" and "50 grupos" in resultado.mensagem
    assert resultado.dados is None


def test_mesmo_dia_em_prioridades_distintas_e_valido_mas_ponto_duplicado_e_rejeitado(cliente):
    cliente.return_value = [prioridade("0", "Alta"), prioridade("1", "Média")]
    assert consultar(ocorrencia, pedido("VIS-26")).status == "SUCESSO"
    cliente.return_value.append(prioridade("0", "Alta"))
    assert consultar(ocorrencia, pedido("VIS-26")).status == "ERRO_FERRAMENTA"


def test_coluna_de_prioridade_ausente_nao_e_convertida_em_grupo_nulo(cliente):
    linha = prioridade("0", "Alta")
    linha.pop("prioridade_nome")
    cliente.return_value = [linha]
    resultado = consultar(ocorrencia, pedido("VIS-26"))
    assert resultado.status == "ERRO_FERRAMENTA" and resultado.dados is None


def test_alta_prioridade_usa_flag_publicada_e_preserva_zero_real(cliente):
    cliente.return_value = [{"local_id": None, "nome_local": None, "valor": "0", "qtd_registros": "3"}]
    resultado = consultar(ocorrencia, pedido("VIS-27"))
    sql = cliente.await_args.args[0]
    assert "SUM(ocorrencia_alta_prioridade)" in sql
    assert "CASE" not in sql and "prioridade =" not in sql and "esta_ativo =" not in sql
    assert resultado.dados.pontos[0].valor == 0
    assert resultado.dados.pontos[0].grupo == {"local_id": None, "nome_local": None}


def test_filtros_de_ocorrencia_preservam_booleanos_e_valores_parametrizados(cliente):
    consultar(ocorrencia, pedido("VIS-26", filtros={"esta_ativo": False, "prioridade": [0, 2]}))
    sql, parametros = cliente.await_args.args[:2]
    tipos = cliente.await_args.kwargs["tipos_parametros"]
    assert parametros["filtro_0_0"] is False and tipos["filtro_0_0"] == "BOOLEAN"
    assert "prioridade IN (:filtro_1_0, :filtro_1_1)" in sql
    assert tipos["filtro_1_0"] == tipos["filtro_1_1"] == "INT"
    databricks._validar_sql(sql, parametros)


@pytest.mark.parametrize("servico,analise_id", [
    (solicitacao, "VIS-25"), (recorrencia, "VIS-23"), (recorrencia, "VIS-15"),
    (ocorrencia, "VIS-01"),
])
def test_analises_de_outra_fonte_nao_sao_substituidas_por_contagens(cliente, servico, analise_id):
    assert consultar(servico, pedido(analise_id)).status == "ERRO_VALIDACAO"
    cliente.assert_not_awaited()


@pytest.mark.parametrize("servico,analise_id", [(solicitacao, "VIS-09"), (ocorrencia, "VIS-26")])
def test_mes_e_semana_agrupam_na_fonte_sem_reinterpretar_como_dias(cliente, servico, analise_id):
    consulta = pedido(analise_id)
    for granularidade in ("mes", "semana"):
        consulta.granularidade = granularidade
        resultado = consultar(servico, consulta)
        assert resultado.status == "SEM_RESULTADO"
        unidade = "MONTH" if granularidade == "mes" else "WEEK"
        assert f"TRUNC(data_referencia, '{unidade}') AS data_referencia" in cliente.await_args.args[0]
        assert resultado.metadados.granularidade == granularidade


@pytest.mark.parametrize("servico,analise_id", [(solicitacao, "VIS-08"), (recorrencia, "VIS-13"), (ocorrencia, "VIS-26")])
def test_fontes_historicas_nao_recebem_consulta_de_snapshot(cliente, servico, analise_id):
    resultado = consultar(servico, ConsultaVisualizacaoSnapshot(analise_id=analise_id))
    assert resultado.status == "ERRO_VALIDACAO"
    cliente.assert_not_awaited()


@pytest.mark.parametrize("servico,analise_id", [(solicitacao, "VIS-09"), (recorrencia, "VIS-13"), (ocorrencia, "VIS-26")])
def test_timeout_nos_novos_dominios_nao_libera_dados(cliente, servico, analise_id):
    cliente.side_effect = databricks.TimeoutConsultaDatabricks("detalhe interno")
    resultado = consultar(servico, pedido(analise_id))
    assert resultado.status == "TIMEOUT" and resultado.dados is None
    assert "detalhe interno" not in resultado.model_dump_json()
