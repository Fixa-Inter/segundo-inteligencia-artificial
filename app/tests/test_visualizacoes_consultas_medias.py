"""Médias, populações elegíveis e cobertura, sem acesso ao warehouse real."""

import asyncio
from datetime import date
import sqlite3
from unittest.mock import AsyncMock

import pytest

from app.schemas.visualizacao import ConsultaVisualizacaoPeriodo, ResultadoConsultaVisualizacao
from app.services.indicadores.gerais import databricks
from app.services.visualizacoes import os_conclusao, os_criacao, recorrencia, solicitacao


@pytest.fixture(autouse=True)
def cliente(monkeypatch):
    executar = AsyncMock(return_value=[])
    monkeypatch.setattr(databricks, "executar_consulta", executar)
    return executar


def pedido(analise_id, *, filtros=None):
    return ConsultaVisualizacaoPeriodo(
        analise_id=analise_id, periodo={"inicio": "2026-10-01", "fim": "2026-10-04"},
        granularidade="dia" if analise_id in {"VIS-14", "VIS-20"} else None,
        filtros=filtros or {},
    )


def consultar(servico, analise_id, *, filtros=None, unidade_id=7):
    return asyncio.run(servico.consultar(pedido(analise_id, filtros=filtros), unidade_id=unidade_id))


CASOS = [
    (recorrencia, "VIS-14", "episodio_recorrente_pct_item", {"data_referencia": "2026-10-02"}),
    (os_criacao, "VIS-18", "reabertura_pct_item", {"categoria_problema_id": "1", "categoria_problema": "Elétrica"}),
    (os_criacao, "VIS-19", "reatribuicao_pct_item", {"tecnico_id": "9007199254740993", "tecnico_nome": None}),
    (os_conclusao, "VIS-20", "conclusao_prazo_pct_item", {"data_referencia": "2026-10-02"}),
    (os_criacao, "VIS-21", "tempo_pausado_minutos", {"categoria_problema_id": "1", "categoria_problema": "Elétrica"}),
    (solicitacao, "VIS-23", "conversao_os_pct_item", {"categoria_equipamento_id": "3", "categoria_equipamento": "Ar"}),
    (solicitacao, "VIS-24", "reprovacao_pct_item", {"local_id": None, "nome_local": None}),
]


def linha(grupo, *, valor="25.125", elegiveis="3", total="3", negativos="0"):
    return {
        **grupo, "valor": valor, "qtd_registros": elegiveis, "qtd_registros_total": total,
        "qtd_tempos_negativos_excluidos": negativos,
    }


@pytest.mark.parametrize("servico,analise_id,campo,grupo", CASOS)
def test_sete_medias_usam_fonte_medida_e_base_sem_reescalar(cliente, servico, analise_id, campo, grupo):
    cliente.return_value = [linha(grupo)]
    resultado = consultar(servico, analise_id)
    sql, parametros = cliente.await_args.args
    assert resultado.status == "SUCESSO"
    assert f"FROM {servico.FONTE.tabela}" in sql
    assert "AVG(" in sql and campo in sql
    assert "SUM(" not in sql and "* 100" not in sql and "COALESCE" not in sql
    assert "COUNT(*) AS qtd_registros_total" in sql
    assert "WHERE unidade_id = :unidade_id" in sql
    assert parametros["unidade_id"] == 7
    assert parametros["inicio"] == date(2026, 10, 1) and parametros["fim"] == date(2026, 10, 4)
    databricks._validar_sql(sql, parametros)
    assert set(parametros) == set(cliente.await_args.kwargs["tipos_parametros"])
    ponto = next(p for p in resultado.dados.pontos if p.qtd_registros)
    assert ponto.valor == 25.125
    assert ponto.base_calculo.qtd_registros_total == ponto.qtd_registros == 3
    assert resultado.metadados.base_calculo.qtd_registros_elegiveis == 3
    assert resultado.metadados.agregacao == "AVG" and resultado.metadados.campo_valor == campo
    assert resultado.metadados.escala_percentual == (None if analise_id == "VIS-21" else 100)
    assert ResultadoConsultaVisualizacao.model_validate_json(resultado.model_dump_json()) == resultado


@pytest.mark.parametrize("servico,analise_id,campo,grupo", CASOS)
def test_tabela_vazia_difere_de_registros_sem_base(cliente, servico, analise_id, campo, grupo):
    vazio = consultar(servico, analise_id)
    assert vazio.status == "SEM_RESULTADO" and vazio.dados is None
    assert vazio.metadados.base_calculo.qtd_registros_total == 0
    cliente.return_value = [linha(grupo, valor=None, elegiveis="0", total="4")]
    sem_base = consultar(servico, analise_id)
    assert sem_base.status == "SEM_BASE_CALCULO" and sem_base.dados is None
    assert sem_base.metadados.base_calculo.qtd_registros_total == 4
    assert sem_base.metadados.qtd_registros_considerados == 0
    assert sem_base.avisos


@pytest.mark.parametrize("servico,analise_id,campo,grupo", CASOS)
def test_unidade_invalida_impede_consulta_de_medias(cliente, servico, analise_id, campo, grupo):
    assert consultar(servico, analise_id, unidade_id=True).status == "ERRO_VALIDACAO"
    cliente.assert_not_awaited()


def executar_amostra(cliente, fonte, linhas):
    """Executa os agregados reais em SQLite, adaptando apenas tabela e DATE.

    Não substitui verificação do dialeto no Databricks. Evita validar somente
    textos de SQL ou resultados prontos de mocks para as regras de população.
    """
    async def executar(sql, parametros, *, tipos_parametros):
        databricks._validar_sql(sql, parametros)
        assert f"FROM workspace.fixa_pipeline.gold_dashboard_{fonte}" in sql
        sql = sql.replace(f"workspace.fixa_pipeline.gold_dashboard_{fonte}", "amostra")
        for marcador in ("inicio", "fim"):
            sql = sql.replace(f"CAST(:{marcador} AS DATE)", f":{marcador}")
        valores_parametros = {k: v.isoformat() if type(v) is date else v for k, v in parametros.items()}
        with sqlite3.connect(":memory:") as conexao:
            conexao.row_factory = sqlite3.Row
            colunas = list(linhas[0])
            conexao.execute(f"CREATE TABLE amostra ({', '.join(colunas)})")
            conexao.executemany(
                f"INSERT INTO amostra VALUES ({', '.join('?' for _ in colunas)})",
                [tuple(linha[campo] for campo in colunas) for linha in linhas],
            )
            return [dict(linha) for linha in conexao.execute(sql, valores_parametros)]
    cliente.side_effect = executar


def test_prazo_mantem_denominador_total_e_calcula_so_datas_validas_nao_nulas(cliente):
    linhas = [
        {"unidade_id": 7, "data_referencia": "2026-10-01", "datas_prazo_validas": valida,
         "conclusao_prazo_pct_item": valor}
        for valida, valor in [(True, 0), (True, 100), (True, None), (False, 100), (None, 100), (False, None)]
    ]
    linhas += [
        {"unidade_id": 7, "data_referencia": "2026-10-02", "datas_prazo_validas": False,
         "conclusao_prazo_pct_item": 100},
        {"unidade_id": 8, "data_referencia": "2026-10-01", "datas_prazo_validas": True,
         "conclusao_prazo_pct_item": 100},
        {"unidade_id": 7, "data_referencia": "2026-10-04", "datas_prazo_validas": True,
         "conclusao_prazo_pct_item": 100},
    ]
    executar_amostra(cliente, "os_conclusao", linhas)
    resultado = consultar(os_conclusao, "VIS-20")
    sql, parametros = cliente.await_args.args
    assert resultado.status == "SUCESSO_PARCIAL"
    assert [p.valor for p in resultado.dados.pontos] == [50.0, None, None]
    assert [p.qtd_registros for p in resultado.dados.pontos] == [2, 0, 0]
    assert [p.base_calculo.qtd_registros_total for p in resultado.dados.pontos] == [6, 1, 0]
    assert resultado.metadados.base_calculo.qtd_registros_total == 7
    assert resultado.metadados.base_calculo.qtd_registros_elegiveis == 2
    assert resultado.metadados.filtros_aplicados["datas_prazo_validas"] is True
    assert "CASE WHEN datas_prazo_validas = :obrigatorio_0 THEN conclusao_prazo_pct_item END" in sql
    assert "datas_prazo_validas" not in sql.split("WHERE unidade_id", 1)[1]
    assert parametros["obrigatorio_0"] is True
    assert cliente.await_args.kwargs["tipos_parametros"]["obrigatorio_0"] == "BOOLEAN"


def test_media_pausa_exclui_negativos_conta_exclusoes_e_mantem_zero(cliente):
    linhas = [
        {"unidade_id": 7, "data_referencia": "2026-10-02", "categoria_problema_id": 1,
         "categoria_problema": "Elétrica", "tempo_pausado_minutos": valor}
        for valor in [-8, -2, None, 0, 10, 20]
    ]
    executar_amostra(cliente, "os_criacao", linhas)
    resultado = consultar(os_criacao, "VIS-21")
    assert resultado.status == "SUCESSO_PARCIAL"
    ponto = resultado.dados.pontos[0]
    assert ponto.valor == 10 and ponto.qtd_registros == 3
    assert ponto.base_calculo.qtd_registros_total == 6
    assert ponto.base_calculo.qtd_tempos_negativos_excluidos == 2
    assert resultado.metadados.base_calculo.qtd_tempos_negativos_excluidos == 2
    assert any("negativos excluídos: 2" in aviso for aviso in resultado.avisos)


@pytest.mark.parametrize("valores,excluidos", [([-3, -2], 2), ([None, -1], 1), ([None], 0)])
def test_pausa_sem_elegiveis_nao_apresenta_media_zero(cliente, valores, excluidos):
    executar_amostra(cliente, "os_criacao", [
        {"unidade_id": 7, "data_referencia": "2026-10-02", "categoria_problema_id": None,
         "categoria_problema": None, "tempo_pausado_minutos": valor}
        for valor in valores
    ])
    resultado = consultar(os_criacao, "VIS-21")
    assert resultado.status == "SEM_BASE_CALCULO" and resultado.dados is None
    assert resultado.metadados.base_calculo.qtd_tempos_negativos_excluidos == excluidos


@pytest.mark.parametrize("analise_id,campo", [("VIS-18", "reabertura_pct_item"), ("VIS-19", "reatribuicao_pct_item")])
def test_percentuais_usam_linhas_elegiveis_e_grupos_preservam_ids(cliente, analise_id, campo):
    grupo = {"categoria_problema_id": 1, "categoria_problema": "Elétrica"} if analise_id == "VIS-18" else {
        "tecnico_id": 1, "tecnico_nome": "Pessoa",
    }
    executar_amostra(cliente, "os_criacao", [
        {"unidade_id": 7, "data_referencia": "2026-10-02", **grupo, campo: valor}
        for valor in [0, 100, 100, None]
    ])
    resultado = consultar(os_criacao, analise_id)
    assert resultado.dados.pontos[0].valor == pytest.approx(200 / 3)
    assert resultado.dados.pontos[0].qtd_registros == 3
    assert resultado.metadados.base_calculo.qtd_registros_total == 4


def test_recorrencia_nao_pondera_media_pelo_numero_de_solicitacoes(cliente):
    executar_amostra(cliente, "recorrencia", [
        {"unidade_id": 7, "data_referencia": "2026-10-02", "local_id": "001",
         "episodio_recorrente_pct_item": valor, "qtd_solicitacoes": quantidade}
        for valor, quantidade in [(0, 1), (100, 20), (None, 30)]
    ])
    resultado = consultar(recorrencia, "VIS-14", filtros={"local_id": "001"})
    assert [p.valor for p in resultado.dados.pontos] == [None, 50, None]
    assert resultado.metadados.base_calculo.qtd_registros_total == 3
    assert resultado.metadados.qtd_registros_considerados == 2
    assert cliente.await_args.kwargs["tipos_parametros"]["filtro_0_0"] == "STRING"


@pytest.mark.parametrize("analise_id,campo,grupo", [
    ("VIS-23", "conversao_os_pct_item", {"categoria_equipamento_id": 3, "categoria_equipamento": "Ar"}),
    ("VIS-24", "reprovacao_pct_item", {"local_id": 4, "nome_local": "Sala"}),
])
def test_taxas_solicitacao_mantem_zero_real_e_excluem_nulos(cliente, analise_id, campo, grupo):
    executar_amostra(cliente, "solicitacao", [
        {"unidade_id": 7, "data_referencia": "2026-10-02", **grupo, campo: valor}
        for valor in [0, None, 0]
    ])
    resultado = consultar(solicitacao, analise_id)
    assert resultado.status == "SUCESSO_PARCIAL"
    assert resultado.dados.pontos[0].valor == 0 and resultado.dados.pontos[0].qtd_registros == 2
    assert resultado.metadados.base_calculo.qtd_registros_total == 3


def test_cobertura_global_soma_bases_sem_media_de_medias_e_mantem_grupo_sem_base(cliente):
    cliente.return_value = [
        linha({"local_id": "1", "nome_local": "Sala"}, valor="100", elegiveis="1", total="1"),
        linha({"local_id": "2", "nome_local": "Sala"}, valor="0", elegiveis="3", total="4"),
        linha({"local_id": None, "nome_local": None}, valor=None, elegiveis="0", total="2"),
    ]
    resultado = consultar(solicitacao, "VIS-24")
    assert resultado.status == "SUCESSO_PARCIAL"
    assert [p.valor for p in resultado.dados.pontos] == [100, 0, None]
    assert resultado.dados.pontos[2].grupo == {"local_id": None, "nome_local": None}
    assert resultado.metadados.base_calculo.qtd_registros_elegiveis == 4
    assert resultado.metadados.base_calculo.qtd_registros_total == 7


@pytest.mark.parametrize("alteracao", [
    {"valor": True}, {"valor": "NaN"}, {"valor": float("inf")}, {"valor": "1e999"},
    {"valor": "1,5"}, {"valor": "1_000"}, {"valor": -1}, {"valor": 100.01},
    {"valor": None}, {"valor": "0", "qtd_registros": "0"},
    {"qtd_registros_total": "2"}, {"qtd_registros_total": "0", "qtd_registros": "0", "valor": None},
    {"qtd_registros": "1.5"}, {"qtd_registros_total": True},
])
def test_medidas_ou_bases_incompativeis_nao_sao_coagidas_zeradas_ou_liberadas(cliente, alteracao):
    cliente.return_value = [{**linha({"local_id": "1", "nome_local": None}), **alteracao}]
    resultado = consultar(solicitacao, "VIS-24")
    assert resultado.status == "ERRO_FERRAMENTA" and resultado.dados is None


@pytest.mark.parametrize("campo", ["qtd_registros_total", "qtd_tempos_negativos_excluidos"])
def test_campo_de_cobertura_ausente_nao_e_inventado(cliente, campo):
    amostra = linha({"categoria_problema_id": None, "categoria_problema": None})
    amostra.pop(campo)
    cliente.return_value = [amostra]
    assert consultar(os_criacao, "VIS-21").status == "ERRO_FERRAMENTA"


def test_media_pausa_negativa_apos_exclusao_e_erro_de_resposta(cliente):
    cliente.return_value = [linha({"categoria_problema_id": None, "categoria_problema": None}, valor="-0.5")]
    assert consultar(os_criacao, "VIS-21").status == "ERRO_FERRAMENTA"


@pytest.mark.parametrize("negativos", ["-1", "1.5", "2"])
def test_contagem_de_negativos_deve_ser_inteira_e_compativel_com_a_base(cliente, negativos):
    cliente.return_value = [linha(
        {"categoria_problema_id": None, "categoria_problema": None},
        elegiveis="2", total="3", negativos=negativos,
    )]
    assert consultar(os_criacao, "VIS-21").status == "ERRO_FERRAMENTA"


def test_negativos_sao_excluidos_apenas_das_analises_aprovadas_da_criacao():
    assert {a.id for a in os_criacao.ANALISES if a.excluir_negativos} == {"VIS-06", "VIS-16", "VIS-17", "VIS-21"}


@pytest.mark.parametrize("analise_id,servico", [("VIS-14", recorrencia), ("VIS-20", os_conclusao)])
def test_percentuais_mensais_agrupam_diretamente_na_fonte(cliente, analise_id, servico):
    consulta = pedido(analise_id)
    consulta.granularidade = "mes"
    assert asyncio.run(servico.consultar(consulta, unidade_id=7)).status == "SEM_RESULTADO"
    assert "AVG(" in cliente.await_args.args[0]
    assert "GROUP BY TRUNC(data_referencia, 'MONTH')" in cliente.await_args.args[0]


def test_categorias_excedentes_nao_entregam_cobertura_parcial_como_total(cliente):
    cliente.return_value = [linha({"local_id": str(i), "nome_local": None}) for i in range(51)]
    resultado = consultar(solicitacao, "VIS-24")
    assert resultado.status == "ERRO_VALIDACAO" and resultado.dados is None and resultado.metadados is None


def test_flag_de_validade_nao_pode_ser_substituida_por_filtro_do_modelo(cliente):
    resultado = consultar(os_conclusao, "VIS-20", filtros={"datas_prazo_validas": False})
    assert resultado.status == "ERRO_VALIDACAO"
    cliente.assert_not_awaited()
