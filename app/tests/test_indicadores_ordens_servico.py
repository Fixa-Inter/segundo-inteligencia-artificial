"""Testes das tools de indicadores de ordens de serviço."""

import asyncio
from datetime import date, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.schemas import UsuarioContexto
from app.services.indicadores import ordem_servico as servico
from app.tools.metricas_kpis import (
    obter_carga_ativa_tecnicos,
    obter_media_tarefas_por_os,
    obter_os_abertas,
    obter_os_atrasadas,
    obter_os_finalizadas,
    obter_produtividade_tecnicos,
    obter_taxa_reatribuicao_os,
    obter_taxa_reabertura_os,
    obter_taxa_atraso_os,
    obter_taxa_conclusao_prazo,
    obter_tempo_medio_espera_os,
    obter_tempo_medio_pausado_os,
    obter_tempo_medio_resolucao_os,
    obter_total_os,
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


def test_tool_total_os_consulta_gold_com_periodo_exclusivo(monkeypatch):
    consulta = executar_com_resultado(monkeypatch, {"total_os": "12"})

    resultado = asyncio.run(obter_total_os.coroutine(
        date(2026, 10, 1), date(2026, 11, 1), runtime(),
    ))

    assert resultado["status"] == "SUCESSO"
    assert resultado["resultado"] == {"total_os": "12"}
    assert resultado["periodo"] == {
        "inicio": "2026-10-01", "fim_exclusivo": "2026-11-01",
    }
    sql, parametros = consulta.await_args.args[:2]
    assert "workspace.gold.kpi_os_criacao_diario" in sql
    assert parametros == {"inicio": date(2026, 10, 1), "fim": date(2026, 11, 1)}


def test_tool_os_abertas_usa_status_atual_sem_periodo(monkeypatch):
    consulta = executar_com_resultado(monkeypatch, {"os_abertas": "8"})

    resultado = asyncio.run(obter_os_abertas.coroutine(runtime()))

    assert resultado["resultado"] == {"os_abertas": "8"}
    sql = consulta.await_args.args[0]
    assert "workspace.gold.os_por_status" in sql
    assert "status_id IN (1, 2, 3)" in sql
    assert consulta.await_args.args[1] == {}


def test_tool_os_atrasadas_separa_status_de_prazo_vencido(monkeypatch):
    consulta = executar_com_resultado(monkeypatch, {"os_atrasadas": "3"})

    resultado = asyncio.run(obter_os_atrasadas.coroutine(runtime()))

    assert resultado["resultado"] == {"os_atrasadas": "3"}
    sql = consulta.await_args.args[0]
    assert "status_id = 1" in sql
    assert "data_prevista" not in sql


def test_tool_taxa_atraso_informa_numerador_e_denominador(monkeypatch):
    consulta = executar_com_resultado(monkeypatch, {
        "atrasadas": "2", "abertas": "5", "taxa_pct": "40.0",
    })

    resultado = asyncio.run(obter_taxa_atraso_os.coroutine(runtime()))

    assert resultado["resultado"]["atrasadas"] == "2"
    assert resultado["resultado"]["abertas"] == "5"
    assert "NULLIF" in consulta.await_args.args[0]


def test_tool_os_finalizadas_filtra_data_de_conclusao(monkeypatch):
    consulta = executar_com_resultado(monkeypatch, {"os_finalizadas": "4"})

    resultado = asyncio.run(obter_os_finalizadas.coroutine(
        date(2026, 10, 1), date(2026, 11, 1), runtime(),
    ))

    assert resultado["resultado"] == {"os_finalizadas": "4"}
    assert "workspace.gold.kpi_os_conclusao_diario" in consulta.await_args.args[0]
    assert consulta.await_args.args[1] == {
        "inicio": date(2026, 10, 1), "fim": date(2026, 11, 1),
    }


def test_tool_taxa_conclusao_prazo_preserva_cobertura_e_denominador(monkeypatch):
    consulta = executar_com_resultado(monkeypatch, {
        "finalizadas": "10", "elegiveis": "8", "no_prazo": "6", "taxa_pct": "75.0",
    })

    resultado = asyncio.run(obter_taxa_conclusao_prazo.coroutine(
        date(2026, 10, 1), date(2026, 11, 1), runtime(),
    ))

    assert resultado["resultado"]["elegiveis"] == "8"
    assert resultado["resultado"]["taxa_pct"] == "75.0"
    assert "qtd_os_com_prazo_valido" in consulta.await_args.args[0]


def test_tool_tempo_espera_usa_os_tempos_e_timestamps(monkeypatch):
    consulta = executar_com_resultado(monkeypatch, {
        "os_com_espera_valida": "2", "media_minutos": "18.5",
    })

    resultado = asyncio.run(obter_tempo_medio_espera_os.coroutine(
        date(2026, 10, 1), date(2026, 11, 1), runtime(),
    ))

    assert resultado["resultado"]["media_minutos"] == "18.5"
    sql, parametros = consulta.await_args.args[:2]
    assert "workspace.gold.os_tempos" in sql
    assert parametros == {
        "inicio": datetime(2026, 10, 1), "fim": datetime(2026, 11, 1),
    }
    assert consulta.await_args.kwargs["tipos_parametros"] == {
        "inicio": "TIMESTAMP", "fim": "TIMESTAMP",
    }


def test_tools_bloqueiam_perfil_nao_gestor(monkeypatch):
    consulta = AsyncMock()
    monkeypatch.setattr(servico, "executar_consulta", consulta)

    resultado = asyncio.run(obter_os_abertas.coroutine(runtime("tecnico")))

    assert resultado["status"] == "ACESSO_NEGADO"
    consulta.assert_not_awaited()


def test_tool_periodo_invertido_retorna_validacao_sem_consultar(monkeypatch):
    consulta = AsyncMock()
    monkeypatch.setattr(servico, "executar_consulta", consulta)

    resultado = asyncio.run(obter_total_os.coroutine(
        date(2026, 11, 1), date(2026, 10, 1), runtime(),
    ))

    assert resultado["status"] == "ERRO_VALIDACAO"
    consulta.assert_not_awaited()


def test_tool_tempo_medio_resolucao_filtra_conclusao_valida(monkeypatch):
    consulta = executar_com_resultado(monkeypatch, {
        "os_com_resolucao_valida": "3", "media_minutos": "75.2",
    })
    resultado = asyncio.run(obter_tempo_medio_resolucao_os.coroutine(
        date(2026, 10, 1), date(2026, 11, 1), runtime(),
    ))
    assert resultado["resultado"]["media_minutos"] == "75.2"
    sql, parametros = consulta.await_args.args[:2]
    assert "data_conclusao >= :inicio" in sql
    assert "data_conclusao >= data_inicio" in sql
    assert parametros == {"inicio": datetime(2026, 10, 1), "fim": datetime(2026, 11, 1)}


def test_tool_tempo_medio_pausado_inclui_zero(monkeypatch):
    consulta = executar_com_resultado(monkeypatch, {
        "os_com_tempo_pausado_valido": "3", "media_minutos": "0",
    })
    resultado = asyncio.run(obter_tempo_medio_pausado_os.coroutine(
        date(2026, 10, 1), date(2026, 11, 1), runtime(),
    ))
    assert resultado["resultado"]["media_minutos"] == "0"
    assert "tempo_pausado_minutos >= 0" in consulta.await_args.args[0]


def test_tool_taxa_reabertura_consulta_coorte_criacao(monkeypatch):
    consulta = executar_com_resultado(monkeypatch, {
        "numerador": "2", "os_criadas": "10", "taxa_pct": "20",
    })
    resultado = asyncio.run(obter_taxa_reabertura_os.coroutine(
        date(2026, 10, 1), date(2026, 11, 1), runtime(),
    ))
    assert resultado["resultado"]["taxa_pct"] == "20"
    assert "SUM(qtd_os_reabertas)" in consulta.await_args.args[0]


def test_tool_taxa_reatribuicao_consulta_coorte_criacao(monkeypatch):
    consulta = executar_com_resultado(monkeypatch, {
        "numerador": "3", "os_criadas": "10", "taxa_pct": "30",
    })
    resultado = asyncio.run(obter_taxa_reatribuicao_os.coroutine(
        date(2026, 10, 1), date(2026, 11, 1), runtime(),
    ))
    assert resultado["resultado"]["taxa_pct"] == "30"
    assert "SUM(qtd_os_reatribuidas)" in consulta.await_args.args[0]


def test_tool_carga_ativa_tecnicos_e_snapshot_sem_periodo(monkeypatch):
    consulta = executar_com_resultado(monkeypatch, {
        "tecnico_id": "7", "tecnico_nome": "Ana", "os_abertas": "4",
    })
    resultado = asyncio.run(obter_carga_ativa_tecnicos.coroutine(runtime()))
    assert resultado["resultados"][0]["os_abertas"] == "4"
    sql, parametros = consulta.await_args.args[:2]
    assert "workspace.gold.kpi_carga_ativa_tecnico" in sql
    assert parametros == {}


def test_tool_produtividade_tecnicos_filtra_data_de_conclusao(monkeypatch):
    consulta = executar_com_resultado(monkeypatch, {
        "tecnico_id": "7", "tecnico_nome": "Ana", "os_finalizadas": "6",
    })
    resultado = asyncio.run(obter_produtividade_tecnicos.coroutine(
        date(2026, 10, 1), date(2026, 11, 1), runtime(),
    ))
    assert resultado["resultados"][0]["os_finalizadas"] == "6"
    assert "workspace.gold.kpi_produtividade_tecnico" in consulta.await_args.args[0]
    assert consulta.await_args.kwargs["tipos_parametros"] == {"inicio": "DATE", "fim": "DATE"}


def test_tool_media_tarefas_os_pondera_por_coorte_e_explica_condicao(monkeypatch):
    consulta = executar_com_resultado(monkeypatch, {
        "os_criadas": "10", "media_tarefas_por_os": "2.5",
    })
    resultado = asyncio.run(obter_media_tarefas_por_os.coroutine(
        date(2026, 10, 1), date(2026, 11, 1), runtime(),
    ))
    assert resultado["resultado"]["media_tarefas_por_os"] == "2.5"
    assert "media_tarefas_por_os * qtd_os_criadas" in consulta.await_args.args[0]
    assert "zero tarefas" in resultado["observacao"]
