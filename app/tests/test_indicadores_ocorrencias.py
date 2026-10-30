"""Testes das tools de indicadores de ocorrências."""

import asyncio
import re
from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.schemas import UsuarioContexto
from app.services.indicadores import ocorrencia as servico
from app.tools.metricas_kpis import contexto
from app.tools.metricas_kpis import (
    obter_ocorrencias_ativas,
    obter_ocorrencias_por_categoria_equipamento,
    obter_ocorrencias_por_categoria_problema,
    obter_ocorrencias_por_local,
    obter_ocorrencias_por_periodo,
    obter_ocorrencias_por_prioridade,
    obter_ocorrencias_por_tecnico,
    obter_ocorrencias_por_unidade,
    obter_taxa_ocorrencias_alta_prioridade,
    obter_total_ocorrencias,
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
    return SimpleNamespace(context={"usuario": usuario, "unidade_id": 999})


@pytest.fixture(autouse=True)
def unidade_autenticada(monkeypatch):
    resolvedor = AsyncMock(return_value=8)
    monkeypatch.setattr(contexto, "obter_unidade_id", resolvedor)
    return resolvedor


def verificar_escopo(consulta, resultado, ferramenta):
    consulta.assert_awaited_once()
    sql, parametros = consulta.await_args.args[:2]
    assert re.findall(r"\bFROM\s+([\w.]+)", sql) == [
        "workspace.fixa_pipeline.gold_kpi_ocorrencias_diario",
    ]
    assert "WHERE unidade_id = :unidade_id" in sql
    assert parametros["unidade_id"] == 8
    assert parametros["inicio"] == date(2026, 10, 1)
    assert parametros["fim"] == date(2026, 11, 1)
    assert "data_referencia >= CAST(:inicio AS DATE)" in sql
    assert "data_referencia < CAST(:fim AS DATE)" in sql
    tipos = consulta.await_args.kwargs["tipos_parametros"]
    assert tipos["unidade_id"] == "BIGINT"
    assert tipos["inicio"] == tipos["fim"] == "DATE"
    assert resultado["unidade_id"] == 8
    assert resultado["periodo"] == {
        "inicio": "2026-10-01", "fim_exclusivo": "2026-11-01",
    }
    assert "unidade_id" not in ferramenta.tool_call_schema.model_json_schema()["properties"]
    assert "workspace.gold." not in sql
    assert "diario2" not in sql


def periodo():
    return date(2026, 10, 1), date(2026, 11, 1)


def consulta_com_linhas(monkeypatch, linhas):
    consulta = AsyncMock(return_value=linhas)
    monkeypatch.setattr(servico, "executar_consulta", consulta)
    return consulta


def test_tool_total_ocorrencias_soma_gold_por_data_de_criacao(monkeypatch, unidade_autenticada):
    consulta = consulta_com_linhas(monkeypatch, [{"total_ocorrencias": "12"}])
    contexto_usuario = runtime()
    resultado = asyncio.run(obter_total_ocorrencias.coroutine(*periodo(), contexto_usuario))
    unidade_autenticada.assert_awaited_once_with(contexto_usuario.context["usuario"])
    assert resultado["resultado"]["total_ocorrencias"] == "12"
    sql, parametros = consulta.await_args.args[:2]
    assert "COALESCE(SUM(qtd_ocorrencias), 0)" in sql
    assert "workspace.fixa_pipeline.gold_kpi_ocorrencias_diario" in sql
    assert parametros == {"inicio": periodo()[0], "fim": periodo()[1], "unidade_id": 8}
    verificar_escopo(consulta, resultado, obter_total_ocorrencias)


def test_tool_ocorrencias_por_tecnico_soma_por_tecnico_id(monkeypatch):
    consulta = consulta_com_linhas(monkeypatch, [{"tecnico_id": "4", "ocorrencias": "5"}])
    resultado = asyncio.run(obter_ocorrencias_por_tecnico.coroutine(*periodo(), runtime()))
    assert resultado["resultados"][0]["ocorrencias"] == "5"
    assert "GROUP BY tecnico_id" in consulta.await_args.args[0]
    verificar_escopo(consulta, resultado, obter_ocorrencias_por_tecnico)


def test_tool_ocorrencias_por_unidade_soma_por_unidade_id(monkeypatch):
    consulta = consulta_com_linhas(monkeypatch, [{"unidade_id": "8", "ocorrencias": "3"}])
    resultado = asyncio.run(obter_ocorrencias_por_unidade.coroutine(*periodo(), runtime()))
    assert resultado["resultados"][0]["unidade_id"] == "8"
    assert "GROUP BY unidade_id" in consulta.await_args.args[0]
    verificar_escopo(consulta, resultado, obter_ocorrencias_por_unidade)


def test_tool_ocorrencias_por_local_soma_por_local_id(monkeypatch):
    consulta = consulta_com_linhas(monkeypatch, [{"local_id": "2", "ocorrencias": "9"}])
    resultado = asyncio.run(obter_ocorrencias_por_local.coroutine(*periodo(), runtime()))
    assert resultado["resultados"][0]["local_id"] == "2"
    assert "GROUP BY local_id" in consulta.await_args.args[0]
    verificar_escopo(consulta, resultado, obter_ocorrencias_por_local)


def test_tool_ocorrencias_por_categoria_problema(monkeypatch):
    consulta = consulta_com_linhas(monkeypatch, [{
        "categoria_problema_id": "3", "ocorrencias": "6",
    }])
    resultado = asyncio.run(
        obter_ocorrencias_por_categoria_problema.coroutine(*periodo(), runtime()),
    )
    assert resultado["resultados"][0]["categoria_problema_id"] == "3"
    assert "GROUP BY categoria_problema_id" in consulta.await_args.args[0]
    verificar_escopo(consulta, resultado, obter_ocorrencias_por_categoria_problema)


def test_tool_ocorrencias_bloqueia_nao_gestor_e_periodo_invalido(monkeypatch, unidade_autenticada):
    consulta = AsyncMock()
    monkeypatch.setattr(servico, "executar_consulta", consulta)
    negado = asyncio.run(obter_total_ocorrencias.coroutine(*periodo(), runtime("tecnico")))
    assert negado["status"] == "ACESSO_NEGADO"
    unidade_autenticada.assert_not_awaited()
    consulta.assert_not_awaited()

    invalido = asyncio.run(obter_total_ocorrencias.coroutine(
        date(2026, 11, 1), date(2026, 10, 1), runtime(),
    ))
    assert invalido["status"] == "ERRO_VALIDACAO"
    consulta.assert_not_awaited()

    unidade_autenticada.side_effect = PermissionError("vínculo ausente")
    negado = asyncio.run(obter_ocorrencias_ativas.coroutine(*periodo(), runtime()))
    assert negado["status"] == "ACESSO_NEGADO"
    consulta.assert_not_awaited()


def test_tool_ocorrencias_por_categoria_equipamento(monkeypatch):
    consulta = consulta_com_linhas(monkeypatch, [{
        "categoria_equipamento_id": "5", "ocorrencias": "7",
    }])
    resultado = asyncio.run(
        obter_ocorrencias_por_categoria_equipamento.coroutine(*periodo(), runtime()),
    )
    assert resultado["resultados"][0]["ocorrencias"] == "7"
    assert "GROUP BY categoria_equipamento_id" in consulta.await_args.args[0]
    verificar_escopo(consulta, resultado, obter_ocorrencias_por_categoria_equipamento)


def test_tool_ocorrencias_por_prioridade_preserva_codigos(monkeypatch):
    consulta = consulta_com_linhas(monkeypatch, [
        {"prioridade": "0", "ocorrencias": "2"},
        {"prioridade": "1", "ocorrencias": "3"},
        {"prioridade": "2", "ocorrencias": "4"},
    ])
    resultado = asyncio.run(obter_ocorrencias_por_prioridade.coroutine(*periodo(), runtime()))
    assert [linha["prioridade"] for linha in resultado["resultados"]] == ["0", "1", "2"]
    assert "GROUP BY prioridade" in consulta.await_args.args[0]
    assert "ORDER BY prioridade" in consulta.await_args.args[0]
    verificar_escopo(consulta, resultado, obter_ocorrencias_por_prioridade)


def test_tool_ocorrencias_ativas_representa_revisao_do_gestor(monkeypatch):
    consulta = consulta_com_linhas(monkeypatch, [{"ocorrencias_ativas": "6"}])
    resultado = asyncio.run(obter_ocorrencias_ativas.coroutine(*periodo(), runtime()))
    assert resultado["resultado"]["ocorrencias_ativas"] == "6"
    assert "revisão/aprovação do gestor" in resultado["indicador"]
    assert "última atualização disponível" in resultado["observacao"]
    assert "final de cada dia passado" in resultado["observacao"]
    assert "estado cadastral" not in resultado["observacao"]
    assert "qtd_ocorrencias_ativas" in consulta.await_args.args[0]
    verificar_escopo(consulta, resultado, obter_ocorrencias_ativas)


def test_tool_taxa_alta_prioridade_calcula_codigo_zero_na_coorte(monkeypatch):
    consulta = consulta_com_linhas(monkeypatch, [{
        "alta": "2", "total": "10", "taxa_pct": "20.0",
    }])
    resultado = asyncio.run(
        obter_taxa_ocorrencias_alta_prioridade.coroutine(*periodo(), runtime()),
    )
    assert resultado["resultado"]["taxa_pct"] == "20.0"
    sql = consulta.await_args.args[0]
    assert "CASE WHEN prioridade = 0" in sql
    assert "NULLIF(SUM(qtd_ocorrencias), 0)" in sql
    verificar_escopo(consulta, resultado, obter_taxa_ocorrencias_alta_prioridade)


def test_tool_ocorrencias_por_periodo_parametriza_granularidade(monkeypatch):
    consulta = consulta_com_linhas(monkeypatch, [{
        "periodo": "2026-10-01", "ocorrencias": "8",
    }])
    resultado = asyncio.run(obter_ocorrencias_por_periodo.coroutine(
        *periodo(), "ano", runtime(),
    ))
    assert resultado["resultados"][0]["ocorrencias"] == "8"
    assert resultado["granularidade"] == "ano"
    sql, parametros = consulta.await_args.args[:2]
    assert "TRUNC(data_referencia, 'YYYY')" in sql
    assert parametros["granularidade"] == "ano"
    assert consulta.await_args.kwargs["tipos_parametros"]["granularidade"] == "STRING"
    verificar_escopo(consulta, resultado, obter_ocorrencias_por_periodo)


def test_service_rejeita_granularidade_ocorrencia_invalida(monkeypatch):
    consulta = AsyncMock()
    monkeypatch.setattr(servico, "executar_consulta", consulta)
    resultado = asyncio.run(servico.obter_ocorrencias_por_periodo(
        *periodo(), "semana", unidade_id=8,
    ))
    assert resultado["status"] == "ERRO_VALIDACAO"
    consulta.assert_not_awaited()
