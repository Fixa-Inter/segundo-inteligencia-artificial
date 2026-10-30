"""Testes das tools de indicadores de ordens de serviço."""

import asyncio
import inspect
import re
from datetime import date, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.schemas import UsuarioContexto
from app.services.indicadores import ordem_servico as servico
from app.services.indicadores import problema as servico_problema
from app.services.indicadores import ocorrencia as servico_ocorrencia
from app.tools.metricas_kpis import contexto
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
    # Um ID solto no contexto não substitui o vínculo resolvido no servidor.
    return SimpleNamespace(context={"usuario": usuario, "unidade_id": 999})


@pytest.fixture(autouse=True)
def unidade_autenticada(monkeypatch):
    resolvedor = AsyncMock(return_value=7)
    monkeypatch.setattr(contexto, "obter_unidade_id", resolvedor)
    return resolvedor


def verificar_escopo(consulta, resultado, tabela):
    consulta.assert_awaited_once()
    sql, parametros = consulta.await_args.args[:2]
    assert re.findall(r"\bFROM\s+([\w.]+)", sql) == [
        f"workspace.fixa_pipeline.{tabela}",
    ]
    assert "WHERE unidade_id = :unidade_id" in sql
    assert parametros["unidade_id"] == 7
    assert consulta.await_args.kwargs["tipos_parametros"]["unidade_id"] == "BIGINT"
    assert resultado["unidade_id"] == 7
    assert "workspace.gold." not in sql
    assert "diario2" not in sql


def executar_com_resultado(monkeypatch, resultado):
    consulta = AsyncMock(return_value=[resultado])
    monkeypatch.setattr(servico, "executar_consulta", consulta)
    return consulta


def test_tool_total_os_consulta_gold_com_periodo_exclusivo(monkeypatch, unidade_autenticada):
    consulta = executar_com_resultado(monkeypatch, {"total_os": "12"})
    contexto_usuario = runtime()

    resultado = asyncio.run(obter_total_os.coroutine(
        date(2026, 10, 1), date(2026, 11, 1), contexto_usuario,
    ))

    unidade_autenticada.assert_awaited_once_with(contexto_usuario.context["usuario"])
    assert "unidade_id" not in obter_total_os.tool_call_schema.model_json_schema()["properties"]
    assert resultado["status"] == "SUCESSO"
    assert resultado["resultado"] == {"total_os": "12"}
    assert resultado["periodo"] == {
        "inicio": "2026-10-01", "fim_exclusivo": "2026-11-01",
    }
    sql, parametros = consulta.await_args.args[:2]
    assert "workspace.fixa_pipeline.gold_kpi_os_criacao_diario" in sql
    assert parametros == {"inicio": date(2026, 10, 1), "fim": date(2026, 11, 1), "unidade_id": 7}
    verificar_escopo(consulta, resultado, "gold_kpi_os_criacao_diario")


def test_tool_os_abertas_usa_status_atual_sem_periodo(monkeypatch):
    consulta = executar_com_resultado(monkeypatch, {"os_abertas": "8"})

    resultado = asyncio.run(obter_os_abertas.coroutine(runtime()))

    assert resultado["resultado"] == {"os_abertas": "8"}
    sql = consulta.await_args.args[0]
    assert "workspace.fixa_pipeline.gold_os_por_status" in sql
    assert "status_id IN (1, 2, 3)" in sql
    assert consulta.await_args.args[1] == {"unidade_id": 7}
    verificar_escopo(consulta, resultado, "gold_os_por_status")


def test_tool_os_atrasadas_separa_status_de_prazo_vencido(monkeypatch):
    consulta = executar_com_resultado(monkeypatch, {"os_atrasadas": "3"})

    resultado = asyncio.run(obter_os_atrasadas.coroutine(runtime()))

    assert resultado["resultado"] == {"os_atrasadas": "3"}
    sql = consulta.await_args.args[0]
    assert "status_id = 1" in sql
    assert "data_prevista" not in sql
    verificar_escopo(consulta, resultado, "gold_os_por_status")


def test_tool_taxa_atraso_informa_numerador_e_denominador(monkeypatch):
    consulta = executar_com_resultado(monkeypatch, {
        "atrasadas": "2", "abertas": "5", "taxa_pct": "40.0",
    })

    resultado = asyncio.run(obter_taxa_atraso_os.coroutine(runtime()))

    assert resultado["resultado"]["atrasadas"] == "2"
    assert resultado["resultado"]["abertas"] == "5"
    assert "NULLIF" in consulta.await_args.args[0]
    verificar_escopo(consulta, resultado, "gold_os_por_status")


def test_tool_os_finalizadas_filtra_data_de_conclusao(monkeypatch):
    consulta = executar_com_resultado(monkeypatch, {"os_finalizadas": "4"})

    resultado = asyncio.run(obter_os_finalizadas.coroutine(
        date(2026, 10, 1), date(2026, 11, 1), runtime(),
    ))

    assert resultado["resultado"] == {"os_finalizadas": "4"}
    assert "workspace.fixa_pipeline.gold_kpi_os_conclusao_diario" in consulta.await_args.args[0]
    assert consulta.await_args.args[1] == {
        "inicio": date(2026, 10, 1), "fim": date(2026, 11, 1), "unidade_id": 7,
    }
    verificar_escopo(consulta, resultado, "gold_kpi_os_conclusao_diario")


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
    verificar_escopo(consulta, resultado, "gold_kpi_os_conclusao_diario")


def test_tool_tempo_espera_usa_os_tempos_e_timestamps(monkeypatch):
    consulta = executar_com_resultado(monkeypatch, {
        "os_com_espera_valida": "2", "media_minutos": "18.5",
    })

    resultado = asyncio.run(obter_tempo_medio_espera_os.coroutine(
        date(2026, 10, 1), date(2026, 11, 1), runtime(),
    ))

    assert resultado["resultado"]["media_minutos"] == "18.5"
    sql, parametros = consulta.await_args.args[:2]
    assert "workspace.fixa_pipeline.gold_os_tempos" in sql
    assert parametros == {
        "inicio": datetime(2026, 10, 1), "fim": datetime(2026, 11, 1), "unidade_id": 7,
    }
    assert consulta.await_args.kwargs["tipos_parametros"] == {
        "inicio": "TIMESTAMP", "fim": "TIMESTAMP", "unidade_id": "BIGINT",
    }
    verificar_escopo(consulta, resultado, "gold_os_tempos")


def test_tools_bloqueiam_contexto_ou_unidade_nao_autorizados(monkeypatch, unidade_autenticada):
    consulta = AsyncMock()
    monkeypatch.setattr(servico, "executar_consulta", consulta)

    usuario_invalido = runtime()
    usuario_invalido.context["usuario"] = usuario_invalido.context["usuario"].model_copy(
        update={"usuario_id": 0},
    )
    for invalido in (
        None, SimpleNamespace(), SimpleNamespace(context=None),
        SimpleNamespace(context={}), SimpleNamespace(context={"usuario": {}}),
        runtime("tecnico"), runtime("solicitante"), runtime("administrador"),
        usuario_invalido,
    ):
        resultado = asyncio.run(obter_os_abertas.coroutine(invalido))
        assert resultado["status"] == "ACESSO_NEGADO"
    unidade_autenticada.assert_not_awaited()

    for unidade in (None, True, False, 0, -1, "7", 7.0):
        unidade_autenticada.return_value = unidade
        resultado = asyncio.run(obter_os_abertas.coroutine(runtime()))
        assert resultado["status"] == "ACESSO_NEGADO"
        assert "unidade_id" not in resultado

    for erro, status in (
        (PermissionError("vínculo ausente"), "ACESSO_NEGADO"),
        (ValueError("usuário inválido"), "ACESSO_NEGADO"),
        (RuntimeError("credencial-privada"), "ERRO_FERRAMENTA"),
    ):
        unidade_autenticada.side_effect = erro
        resultado = asyncio.run(obter_os_abertas.coroutine(runtime()))
        assert resultado["status"] == status
        assert "credencial-privada" not in str(resultado)
    consulta.assert_not_awaited()


def test_servicos_indicadores_exigem_unidade_valida_antes_de_consultar(monkeypatch):
    consulta = AsyncMock()
    monkeypatch.setattr(servico, "executar_consulta", consulta)
    monkeypatch.setattr(servico_problema, "executar_consulta", consulta)
    monkeypatch.setattr(servico_ocorrencia, "executar_consulta", consulta)
    nomes = (
        "obter_total_os", "obter_os_abertas", "obter_os_atrasadas",
        "obter_taxa_atraso_os", "obter_os_finalizadas", "obter_taxa_conclusao_prazo",
        "obter_tempo_medio_espera_os", "obter_tempo_medio_resolucao_os",
        "obter_tempo_medio_pausado_os", "obter_taxa_reabertura_os",
        "obter_taxa_reatribuicao_os", "obter_carga_ativa_tecnicos",
        "obter_produtividade_tecnicos", "obter_media_tarefas_por_os",
    )
    funcoes = [getattr(servico, nome) for nome in nomes]
    funcoes.extend(
        funcao for nome, funcao in inspect.getmembers(servico_problema, inspect.iscoroutinefunction)
        if nome.startswith("obter_")
    )
    funcoes.extend(
        funcao for nome, funcao in inspect.getmembers(servico_ocorrencia, inspect.iscoroutinefunction)
        if nome.startswith("obter_")
    )
    assert len(funcoes) == 36
    for funcao in funcoes:
        parametros = inspect.signature(funcao).parameters
        datas = (date(2026, 10, 1), date(2026, 11, 1)) if "inicio" in parametros else ()
        if "granularidade" in parametros:
            datas = (*datas, "mes")
        with pytest.raises(TypeError, match="unidade_id"):
            funcao(*datas)
        for unidade in (None, True, False, 0, -1, "7", 7.0):
            resultado = asyncio.run(funcao(*datas, unidade_id=unidade))
            assert resultado["status"] == "ERRO_VALIDACAO", funcao.__name__
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
    assert parametros == {"inicio": datetime(2026, 10, 1), "fim": datetime(2026, 11, 1), "unidade_id": 7}
    verificar_escopo(consulta, resultado, "gold_os_tempos")


def test_tool_tempo_medio_pausado_inclui_zero(monkeypatch):
    consulta = executar_com_resultado(monkeypatch, {
        "os_com_tempo_pausado_valido": "3", "media_minutos": "0",
    })
    resultado = asyncio.run(obter_tempo_medio_pausado_os.coroutine(
        date(2026, 10, 1), date(2026, 11, 1), runtime(),
    ))
    assert resultado["resultado"]["media_minutos"] == "0"
    assert "tempo_pausado_minutos >= 0" in consulta.await_args.args[0]
    verificar_escopo(consulta, resultado, "gold_os_tempos")


def test_tool_taxa_reabertura_consulta_coorte_criacao(monkeypatch):
    consulta = executar_com_resultado(monkeypatch, {
        "numerador": "2", "os_criadas": "10", "taxa_pct": "20",
    })
    resultado = asyncio.run(obter_taxa_reabertura_os.coroutine(
        date(2026, 10, 1), date(2026, 11, 1), runtime(),
    ))
    assert resultado["resultado"]["taxa_pct"] == "20"
    assert "SUM(qtd_os_reabertas)" in consulta.await_args.args[0]
    verificar_escopo(consulta, resultado, "gold_kpi_os_criacao_diario")


def test_tool_taxa_reatribuicao_consulta_coorte_criacao(monkeypatch):
    consulta = executar_com_resultado(monkeypatch, {
        "numerador": "3", "os_criadas": "10", "taxa_pct": "30",
    })
    resultado = asyncio.run(obter_taxa_reatribuicao_os.coroutine(
        date(2026, 10, 1), date(2026, 11, 1), runtime(),
    ))
    assert resultado["resultado"]["taxa_pct"] == "30"
    assert "SUM(qtd_os_reatribuidas)" in consulta.await_args.args[0]
    verificar_escopo(consulta, resultado, "gold_kpi_os_criacao_diario")


def test_tool_carga_ativa_tecnicos_e_snapshot_sem_periodo(monkeypatch):
    consulta = executar_com_resultado(monkeypatch, {
        "tecnico_id": "7", "tecnico_nome": "Ana", "os_abertas": "4",
    })
    resultado = asyncio.run(obter_carga_ativa_tecnicos.coroutine(runtime()))
    assert resultado["resultados"][0]["os_abertas"] == "4"
    sql, parametros = consulta.await_args.args[:2]
    assert "workspace.fixa_pipeline.gold_kpi_carga_ativa_tecnico" in sql
    assert parametros == {"unidade_id": 7}
    verificar_escopo(consulta, resultado, "gold_kpi_carga_ativa_tecnico")


def test_tool_produtividade_tecnicos_filtra_data_de_conclusao(monkeypatch):
    consulta = executar_com_resultado(monkeypatch, {
        "tecnico_id": "7", "tecnico_nome": "Ana", "os_finalizadas": "6",
    })
    resultado = asyncio.run(obter_produtividade_tecnicos.coroutine(
        date(2026, 10, 1), date(2026, 11, 1), runtime(),
    ))
    assert resultado["resultados"][0]["os_finalizadas"] == "6"
    assert "workspace.fixa_pipeline.gold_kpi_produtividade_tecnico" in consulta.await_args.args[0]
    assert consulta.await_args.kwargs["tipos_parametros"] == {"inicio": "DATE", "fim": "DATE", "unidade_id": "BIGINT"}
    verificar_escopo(consulta, resultado, "gold_kpi_produtividade_tecnico")


def test_tool_media_tarefas_os_indisponivel_sem_contagens_do_bi(monkeypatch):
    consulta = executar_com_resultado(monkeypatch, {
        "os_criadas": "10", "media_tarefas_por_os": "2.5",
    })
    resultado = asyncio.run(obter_media_tarefas_por_os.coroutine(
        date(2026, 10, 1), date(2026, 11, 1), runtime(),
    ))
    assert resultado["status"] == "INDICADOR_INDISPONIVEL"
    assert resultado["resultado"] == {
        "os_criadas": None, "media_tarefas_por_os": None,
    }
    assert resultado["unidade_id"] == 7
    assert resultado["periodo"] == {
        "inicio": "2026-10-01", "fim_exclusivo": "2026-11-01",
    }
    assert "OS com tarefas" in resultado["indicador"]
    assert "BI" in resultado["mensagem"]
    assert "unidade_id" not in obter_media_tarefas_por_os.tool_call_schema.model_json_schema()["properties"]
    consulta.assert_not_awaited()
