"""Testes das tools de indicadores de problemas/solicitações."""

import asyncio
from datetime import date
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.schemas import UsuarioContexto
from app.services.indicadores import problema as servico
from app.tools.metricas_kpis import (
    obter_solicitacoes_aprovadas,
    obter_solicitacoes_por_categoria_equipamento,
    obter_solicitacoes_por_local,
    obter_solicitacoes_por_periodo,
    obter_solicitacoes_por_unidade,
    obter_solicitacoes_pendentes,
    obter_solicitacoes_reprovadas,
    obter_taxa_aprovacao_solicitacoes,
    obter_taxa_conversao_solicitacoes_os,
    obter_taxa_reprovacao_solicitacoes,
    obter_taxa_recorrencia_local_categoria,
    obter_total_solicitacoes,
)


def runtime(perfil="gestor"):
    usuario = UsuarioContexto(
        access_token="token-de-teste",
        usuario_id=10,
        nome_completo="Gestor de teste",
        email="gestor@example.com",
        tipo_acesso=perfil,
        cnpj_endereco="12345678000195",
    )
    return SimpleNamespace(context={"usuario": usuario})


def executar_com_resultado(monkeypatch, resultado):
    consulta = AsyncMock(return_value=[resultado])
    monkeypatch.setattr(servico, "executar_consulta", consulta)
    return consulta


def periodo():
    return date(2026, 10, 1), date(2026, 11, 1)


def test_tool_total_solicitacoes_soma_coorte_de_criacao(monkeypatch):
    consulta = executar_com_resultado(monkeypatch, {"total_solicitacoes": "15"})
    resultado = asyncio.run(obter_total_solicitacoes.coroutine(*periodo(), runtime()))
    assert resultado["resultado"]["total_solicitacoes"] == "15"
    sql, parametros = consulta.await_args.args[:2]
    assert "SUM(qtd_solicitacoes)" in sql
    assert "workspace.gold.kpi_solicitacoes_diario" in sql
    assert parametros == {"inicio": periodo()[0], "fim": periodo()[1]}


def test_tool_solicitacoes_pendentes_retraz_status_atual_da_coorte(monkeypatch):
    consulta = executar_com_resultado(monkeypatch, {"pendentes": "3"})
    resultado = asyncio.run(obter_solicitacoes_pendentes.coroutine(*periodo(), runtime()))
    assert resultado["resultado"]["pendentes"] == "3"
    assert "SUM(qtd_solicitacoes_pendentes)" in consulta.await_args.args[0]


def test_tool_solicitacoes_aprovadas_retraz_status_atual_da_coorte(monkeypatch):
    consulta = executar_com_resultado(monkeypatch, {"aprovadas": "9"})
    resultado = asyncio.run(obter_solicitacoes_aprovadas.coroutine(*periodo(), runtime()))
    assert resultado["resultado"]["aprovadas"] == "9"
    assert "SUM(qtd_solicitacoes_aprovadas)" in consulta.await_args.args[0]


def test_tool_solicitacoes_reprovadas_retraz_status_atual_da_coorte(monkeypatch):
    consulta = executar_com_resultado(monkeypatch, {"reprovadas": "2"})
    resultado = asyncio.run(obter_solicitacoes_reprovadas.coroutine(*periodo(), runtime()))
    assert resultado["resultado"]["reprovadas"] == "2"
    assert "SUM(qtd_solicitacoes_reprovadas)" in consulta.await_args.args[0]


def test_tool_taxa_aprovacao_usa_todas_as_solicitacoes_como_base(monkeypatch):
    consulta = executar_com_resultado(monkeypatch, {
        "aprovadas": "8", "total": "10", "taxa_pct": "80",
    })
    resultado = asyncio.run(obter_taxa_aprovacao_solicitacoes.coroutine(*periodo(), runtime()))
    assert resultado["resultado"]["taxa_pct"] == "80"
    sql = consulta.await_args.args[0]
    assert "SUM(qtd_solicitacoes_aprovadas)" in sql
    assert "NULLIF(SUM(qtd_solicitacoes), 0)" in sql


def test_tool_taxa_reprovacao_usa_todas_as_solicitacoes_como_base(monkeypatch):
    consulta = executar_com_resultado(monkeypatch, {
        "reprovadas": "2", "total": "10", "taxa_pct": "20",
    })
    resultado = asyncio.run(obter_taxa_reprovacao_solicitacoes.coroutine(*periodo(), runtime()))
    assert resultado["resultado"]["taxa_pct"] == "20"
    sql = consulta.await_args.args[0]
    assert "SUM(qtd_solicitacoes_reprovadas)" in sql
    assert "NULLIF(SUM(qtd_solicitacoes), 0)" in sql


def test_tool_taxa_conversao_conta_solicitacao_uma_vez(monkeypatch):
    consulta = executar_com_resultado(monkeypatch, {
        "com_os": "4", "total": "10", "taxa_pct": "40",
    })
    resultado = asyncio.run(obter_taxa_conversao_solicitacoes_os.coroutine(*periodo(), runtime()))
    assert resultado["resultado"]["taxa_pct"] == "40"
    sql = consulta.await_args.args[0]
    assert "SUM(qtd_solicitacoes_com_os)" in sql
    assert "NULLIF(SUM(qtd_solicitacoes), 0)" in sql


def test_tool_problema_exige_periodo_e_perfil_gestor(monkeypatch):
    consulta = AsyncMock()
    monkeypatch.setattr(servico, "executar_consulta", consulta)
    negado = asyncio.run(obter_total_solicitacoes.coroutine(*periodo(), runtime("tecnico")))
    assert negado["status"] == "ACESSO_NEGADO"
    consulta.assert_not_awaited()

    invalido = asyncio.run(obter_total_solicitacoes.coroutine(
        date(2026, 11, 1), date(2026, 10, 1), runtime(),
    ))
    assert invalido["status"] == "ERRO_VALIDACAO"
    consulta.assert_not_awaited()


def test_tool_solicitacoes_por_unidade_retorna_ids_sem_nome(monkeypatch):
    consulta = AsyncMock(return_value=[{"unidade_id": "21", "solicitacoes": "7"}])
    monkeypatch.setattr(servico, "executar_consulta", consulta)
    resultado = asyncio.run(obter_solicitacoes_por_unidade.coroutine(*periodo(), runtime()))
    assert resultado["resultados"][0] == {"unidade_id": "21", "solicitacoes": "7"}
    assert "GROUP BY unidade_id" in consulta.await_args.args[0]


def test_tool_solicitacoes_por_local_retorna_ids_sem_nome_tipo(monkeypatch):
    consulta = AsyncMock(return_value=[{"local_id": "31", "solicitacoes": "5"}])
    monkeypatch.setattr(servico, "executar_consulta", consulta)
    resultado = asyncio.run(obter_solicitacoes_por_local.coroutine(*periodo(), runtime()))
    assert resultado["resultados"][0]["local_id"] == "31"
    assert "GROUP BY local_id" in consulta.await_args.args[0]


def test_tool_solicitacoes_por_categoria_equipamento(monkeypatch):
    consulta = AsyncMock(return_value=[{
        "categoria_equipamento_id": "9", "solicitacoes": "4",
    }])
    monkeypatch.setattr(servico, "executar_consulta", consulta)
    resultado = asyncio.run(
        obter_solicitacoes_por_categoria_equipamento.coroutine(*periodo(), runtime()),
    )
    assert resultado["resultados"][0]["categoria_equipamento_id"] == "9"
    assert "GROUP BY categoria_equipamento_id" in consulta.await_args.args[0]


def test_tool_solicitacoes_por_periodo_parametriza_granularidade(monkeypatch):
    consulta = AsyncMock(return_value=[{"periodo": "2026-10-01", "solicitacoes": "6"}])
    monkeypatch.setattr(servico, "executar_consulta", consulta)
    resultado = asyncio.run(obter_solicitacoes_por_periodo.coroutine(
        *periodo(), "mes", runtime(),
    ))
    assert resultado["resultados"][0]["solicitacoes"] == "6"
    assert resultado["granularidade"] == "mes"
    sql, parametros = consulta.await_args.args[:2]
    assert "TRUNC(data_referencia, 'MM')" in sql
    assert parametros["granularidade"] == "mes"
    assert consulta.await_args.kwargs["tipos_parametros"]["granularidade"] == "STRING"


def test_service_rejeita_granularidade_inesperada_sem_consultar(monkeypatch):
    consulta = AsyncMock()
    monkeypatch.setattr(servico, "executar_consulta", consulta)
    resultado = asyncio.run(servico.obter_solicitacoes_por_periodo(
        *periodo(), "semana",
    ))
    assert resultado["status"] == "ERRO_VALIDACAO"
    consulta.assert_not_awaited()


def test_tool_taxa_recorrencia_agrupa_par_local_categoria_e_usa_timestamps(monkeypatch):
    consulta = AsyncMock(return_value=[{
        "local_id": "31",
        "categoria_equipamento_id": "9",
        "solicitacoes_nos_episodios": "12",
        "episodios": "5",
        "episodios_recorrentes": "2",
        "taxa_pct": "40.0",
    }])
    monkeypatch.setattr(servico, "executar_consulta", consulta)

    resultado = asyncio.run(obter_taxa_recorrencia_local_categoria.coroutine(
        *periodo(), runtime(),
    ))

    assert resultado["resultados"][0]["taxa_pct"] == "40.0"
    assert "24 horas" in resultado["observacao"]
    sql, parametros = consulta.await_args.args[:2]
    assert "workspace.gold.recorrencia_episodios" in sql
    assert "COUNT(*) FILTER (WHERE recorrente = TRUE)" in sql
    assert "GROUP BY local_id, categoria_equipamento_id" in sql
    assert parametros == {
        "inicio": datetime(2026, 10, 1),
        "fim": datetime(2026, 11, 1),
    }
    assert consulta.await_args.kwargs["tipos_parametros"] == {
        "inicio": "TIMESTAMP", "fim": "TIMESTAMP",
    }
