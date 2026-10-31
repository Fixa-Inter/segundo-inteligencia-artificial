"""Calendários, agregações e preenchimento de séries temporais."""

import asyncio
from datetime import date, timedelta
import sqlite3
from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError

from app.schemas.visualizacao import (
    ConsultaVisualizacaoPeriodo, PeriodoSerieTemporal, PeriodoVisualizacao,
    PontoSerieTemporal, ResultadoConsultaVisualizacao,
)
from app.services.indicadores.gerais import databricks
from app.services.visualizacoes import ocorrencia, os_conclusao, os_criacao, recorrencia, solicitacao

from app.services.visualizacoes.temporais import (
    calendario_consulta, expressao_periodo_sql, inicio_periodo, proximo_periodo,
)


@pytest.fixture(autouse=True)
def cliente(monkeypatch):
    executar = AsyncMock(return_value=[])
    monkeypatch.setattr(databricks, "executar_consulta", executar)
    return executar


def pedido(analise_id, granularidade, inicio="2026-10-05", fim="2026-10-08", filtros=None):
    return ConsultaVisualizacaoPeriodo(
        analise_id=analise_id, granularidade=granularidade, periodo={"inicio": inicio, "fim": fim},
        filtros=filtros or {},
    )


def consultar(servico, consulta, unidade_id=7):
    return asyncio.run(servico.consultar(consulta, unidade_id=unidade_id))


def linha(campo, valor, dia="2026-10-05", **extras):
    return {"unidade_id": 7, "data_referencia": dia, campo: valor, **extras}


def executar_amostra(cliente, fonte, linhas):
    """Executa agregados reais em SQLite, adaptando tabela, DATE e TRUNC.

    A função de calendário é emulada; não certifica o dialeto do Databricks.
    """
    def truncar(valor, unidade):
        dia = date.fromisoformat(valor)
        if unidade == "WEEK":
            return (dia - timedelta(days=dia.weekday())).isoformat()
        if unidade == "MONTH":
            return dia.replace(day=1).isoformat()
        raise ValueError("Unidade não prevista na amostra.")

    async def executar(sql, parametros, *, tipos_parametros):
        databricks._validar_sql(sql, parametros)
        assert set(parametros) == set(tipos_parametros)
        assert f"FROM workspace.fixa_pipeline.gold_dashboard_{fonte}" in sql
        sql = sql.replace(f"workspace.fixa_pipeline.gold_dashboard_{fonte}", "amostra")
        for marcador in ("inicio", "fim"):
            sql = sql.replace(f"CAST(:{marcador} AS DATE)", f":{marcador}")
        parametros = {k: v.isoformat() if type(v) is date else v for k, v in parametros.items()}
        with sqlite3.connect(":memory:") as conexao:
            conexao.row_factory = sqlite3.Row
            conexao.create_function("TRUNC", 2, truncar)
            colunas = list(linhas[0])
            conexao.execute(f"CREATE TABLE amostra ({', '.join(colunas)})")
            conexao.executemany(
                f"INSERT INTO amostra VALUES ({', '.join('?' for _ in colunas)})",
                [tuple(linha[c] for c in colunas) for linha in linhas],
            )
            return [dict(linha) for linha in conexao.execute(sql, parametros)]
    cliente.side_effect = executar


CASOS = [
    (os_criacao, "VIS-01", "qtd_os", False),
    (os_conclusao, "VIS-02", "qtd_os_finalizadas", False),
    (solicitacao, "VIS-09", "qtd_solicitacoes", False),
    (recorrencia, "VIS-14", "episodio_recorrente_pct_item", True),
    (os_conclusao, "VIS-20", "conclusao_prazo_pct_item", True),
    (ocorrencia, "VIS-26", "qtd_ocorrencias", False),
]


@pytest.mark.parametrize("servico,analise_id,campo,percentual", CASOS)
@pytest.mark.parametrize("granularidade", ["dia", "semana", "mes"])
def test_seis_series_em_tres_granularidades_calculam_na_fonte(cliente, servico, analise_id, campo, percentual, granularidade):
    extras = {"datas_prazo_validas": True} if analise_id == "VIS-20" else {}
    if analise_id == "VIS-26":
        extras.update(prioridade=None, prioridade_nome=None)
    executar_amostra(cliente, servico.FONTE.id, [
        linha(campo, 0 if percentual else 1, **extras),
        linha(campo, 100 if percentual else 1, "2026-10-06", **extras),
    ])
    resultado = consultar(servico, pedido(analise_id, granularidade))
    assert resultado.status == "SUCESSO"
    assert resultado.metadados.granularidade == granularidade
    assert resultado.metadados.qtd_registros_considerados == 2
    if granularidade == "dia":
        assert [p.valor for p in resultado.dados.pontos] == ([0, 100, None] if percentual else [1, 1, 0])
        assert all(not p.periodo.parcial for p in resultado.dados.pontos)
    else:
        assert [p.valor for p in resultado.dados.pontos] == ([50] if percentual else [2])
        assert resultado.dados.pontos[0].periodo.parcial
        assert "parciais" in resultado.mensagem
        unidade = "WEEK" if granularidade == "semana" else "MONTH"
        sql = cliente.await_args.args[0]
        assert f"GROUP BY TRUNC(data_referencia, '{unidade}')" in sql
        assert "data_referencia >= CAST(:inicio AS DATE)" in sql
        assert "data_referencia < CAST(:fim AS DATE)" in sql
    assert all(p.periodo is not None for p in resultado.dados.pontos)
    assert ResultadoConsultaVisualizacao.model_validate_json(resultado.model_dump_json()) == resultado


def test_semanas_parciais_nao_ampliam_unidade_ou_datas_solicitadas(cliente):
    linhas = [linha("qtd_os", 1, dia) for dia in ["2026-10-07", "2026-10-08", "2026-10-12", "2026-10-20"]]
    linhas += [linha("qtd_os", 100, "2026-10-06"), linha("qtd_os", 100, "2026-10-21")]
    linhas += [linha("qtd_os", 100, "2026-10-08", unidade_id=8)]
    executar_amostra(cliente, "os_criacao", linhas)
    resultado = consultar(os_criacao, pedido("VIS-01", "semana", "2026-10-07", "2026-10-21"))
    pontos = resultado.dados.pontos
    assert [p.data_referencia for p in pontos] == [date(2026, 10, d) for d in (5, 12, 19)]
    assert [p.valor for p in pontos] == [2, 1, 1]
    assert [p.periodo.parcial for p in pontos] == [True, False, True]
    assert pontos[0].periodo.consultado.inicio == date(2026, 10, 7)
    assert pontos[-1].periodo.consultado.fim == date(2026, 10, 21)
    assert resultado.metadados.periodo.inicio == date(2026, 10, 7)
    assert resultado.metadados.qtd_registros_considerados == 4


def test_meses_parciais_com_mes_vazio_preservam_recorte_e_distincao_de_parcial(cliente):
    executar_amostra(cliente, "solicitacao", [
        linha("qtd_solicitacoes", 1, "2026-10-08"), linha("qtd_solicitacoes", 1, "2026-10-09"),
        linha("qtd_solicitacoes", 1, "2026-12-10"), linha("qtd_solicitacoes", 100, "2026-12-20"),
    ])
    resultado = consultar(solicitacao, pedido("VIS-09", "mes", "2026-10-07", "2026-12-20"))
    pontos = resultado.dados.pontos
    assert [p.valor for p in pontos] == [2, 0, 1]
    assert [p.periodo.parcial for p in pontos] == [True, False, True]
    assert pontos[0].periodo.calendario.inicio == date(2026, 10, 1)
    assert pontos[0].periodo.consultado.inicio == date(2026, 10, 7)
    assert pontos[-1].periodo.calendario.fim == date(2027, 1, 1)
    assert pontos[-1].periodo.consultado.fim == date(2026, 12, 20)


@pytest.mark.parametrize("granularidade,inicio,fim,ultimo", [
    ("semana", "2026-10-05", "2026-10-19", date(2026, 10, 12)),
    ("mes", "2026-10-01", "2026-12-01", date(2026, 11, 1)),
])
def test_fim_exclusivo_alinhado_nao_cria_proximo_periodo(cliente, granularidade, inicio, fim, ultimo):
    executar_amostra(cliente, "os_criacao", [linha("qtd_os", 1, inicio), linha("qtd_os", 100, fim)])
    resultado = consultar(os_criacao, pedido("VIS-01", granularidade, inicio, fim))
    assert resultado.dados.pontos[-1].data_referencia == ultimo
    assert all(not p.periodo.parcial for p in resultado.dados.pontos)
    assert sum(p.valor for p in resultado.dados.pontos) == 1


def test_semana_de_janeiro_pode_ter_referencia_no_ano_anterior(cliente):
    executar_amostra(cliente, "os_criacao", [linha("qtd_os", 1, "2027-01-01"), linha("qtd_os", 1, "2027-01-04")])
    resultado = consultar(os_criacao, pedido("VIS-01", "semana", "2027-01-01", "2027-01-05"))
    assert [p.data_referencia for p in resultado.dados.pontos] == [date(2026, 12, 28), date(2027, 1, 4)]
    assert all(p.periodo.parcial for p in resultado.dados.pontos)


@pytest.mark.parametrize("granularidade,inicio,fim,primeiro,ultimo", [
    ("semana", "2026-10-05", "2026-10-26", "2026-10-06", "2026-10-21"),
    ("mes", "2026-10-01", "2027-01-01", "2026-10-06", "2026-12-21"),
])
def test_percentuais_agregam_linhas_sem_media_de_medias_e_lacunas_sao_nulas(cliente, granularidade, inicio, fim, primeiro, ultimo):
    campo = "episodio_recorrente_pct_item"
    seguinte = (date.fromisoformat(primeiro) + timedelta(days=1)).isoformat()
    linhas = [linha(campo, 0, primeiro)]
    linhas += [linha(campo, v, seguinte) for v in [100, 100, 100, None]]
    linhas += [linha(campo, 0, ultimo)]
    executar_amostra(cliente, "recorrencia", linhas)
    resultado = consultar(recorrencia, pedido("VIS-14", granularidade, inicio, fim))
    assert resultado.status == "SUCESSO_PARCIAL"
    assert [p.valor for p in resultado.dados.pontos] == [75, None, 0]
    assert [p.qtd_registros for p in resultado.dados.pontos] == [4, 0, 1]
    assert [p.base_calculo.qtd_registros_total for p in resultado.dados.pontos] == [5, 0, 1]
    assert resultado.metadados.base_calculo.qtd_registros_total == 6
    assert resultado.metadados.qtd_registros_considerados == 5
    assert resultado.metadados.escala_percentual == 100


@pytest.mark.parametrize("granularidade,inicio,fim", [
    ("semana", "2026-10-05", "2026-10-12"), ("mes", "2026-10-01", "2026-11-01"),
])
def test_cobertura_de_prazo_mantem_datas_invalidas_no_total(cliente, granularidade, inicio, fim):
    executar_amostra(cliente, "os_conclusao", [
        linha("conclusao_prazo_pct_item", valor, "2026-10-06", datas_prazo_validas=valida)
        for valida, valor in [(True, 0), (True, 100), (True, None), (False, 100), (None, 100)]
    ])
    resultado = consultar(os_conclusao, pedido("VIS-20", granularidade, inicio, fim))
    assert resultado.dados.pontos[0].valor == 50
    assert resultado.metadados.base_calculo.qtd_registros_total == 5
    assert resultado.metadados.base_calculo.qtd_registros_elegiveis == 2


@pytest.mark.parametrize("granularidade,inicio,fim", [
    ("semana", "2026-10-05", "2026-10-26"), ("mes", "2026-10-01", "2027-01-01"),
])
def test_grupos_de_prioridade_observados_incluem_nulos_sem_inventar_outros(cliente, granularidade, inicio, fim):
    executar_amostra(cliente, "ocorrencia", [
        linha("qtd_ocorrencias", 1, "2026-10-06", prioridade=None, prioridade_nome=None),
        linha("qtd_ocorrencias", 2, "2026-10-07", prioridade=0, prioridade_nome="Alta"),
    ])
    resultado = consultar(ocorrencia, pedido("VIS-26", granularidade, inicio, fim))
    pontos = resultado.dados.pontos
    assert len(pontos) == 6
    assert [p.grupo["prioridade"] for p in pontos] == [None, 0] * 3
    assert [p.valor for p in pontos] == [1, 2, 0, 0, 0, 0]
    assert resultado.metadados.qtd_registros_considerados == 2


@pytest.mark.parametrize("granularidade,fim,status", [
    ("semana", "2026-03-16", "SUCESSO"), ("semana", "2026-03-23", "ERRO_VALIDACAO"),
    ("mes", "2026-11-01", "SUCESSO"), ("mes", "2026-12-01", "ERRO_VALIDACAO"),
])
def test_limite_500_e_global_e_inclui_lacunas_por_grupo(cliente, granularidade, fim, status):
    inicio = "2026-01-05" if granularidade == "semana" else "2026-01-01"
    executar_amostra(cliente, "ocorrencia", [
        linha("qtd_ocorrencias", 1, inicio, prioridade=i, prioridade_nome=str(i)) for i in range(50)
    ])
    resultado = consultar(ocorrencia, pedido("VIS-26", granularidade, inicio, fim))
    assert resultado.status == status
    if status == "SUCESSO":
        assert len(resultado.dados.pontos) == 500
        assert resultado.metadados.qtd_registros_considerados == 50
    else:
        assert resultado.dados is None


@pytest.mark.parametrize("granularidade", ["semana", "mes"])
def test_limite_de_grupos_nao_e_relaxado_com_agregacao(cliente, granularidade):
    executar_amostra(cliente, "ocorrencia", [
        linha("qtd_ocorrencias", 1, prioridade=i, prioridade_nome=str(i)) for i in range(51)
    ])
    assert consultar(ocorrencia, pedido("VIS-26", granularidade)).status == "ERRO_VALIDACAO"


@pytest.mark.parametrize("granularidade", ["semana", "mes"])
def test_fonte_vazia_nao_inventa_calendario(cliente, granularidade):
    resultado = consultar(os_criacao, pedido("VIS-01", granularidade))
    assert resultado.status == "SEM_RESULTADO" and resultado.dados is None


@pytest.mark.parametrize("granularidade,referencia", [
    ("semana", "2026-10-07"), ("semana", "2026-10-12"), ("mes", "2026-10-07"), ("mes", "2026-11-01"),
])
def test_referencias_desalinhadas_ou_fora_do_calendario_nao_sao_arredondadas(cliente, granularidade, referencia):
    cliente.return_value = [{"data_referencia": referencia, "valor": "1", "qtd_registros": "1"}]
    assert consultar(os_criacao, pedido("VIS-01", granularidade)).status == "ERRO_FERRAMENTA"


@pytest.mark.parametrize("granularidade", ["semana", "mes"])
def test_pontos_duplicados_no_mesmo_periodo_sao_erro(cliente, granularidade):
    referencia = "2026-10-05" if granularidade == "semana" else "2026-10-01"
    cliente.return_value = [{"data_referencia": referencia, "valor": "1", "qtd_registros": "1"}] * 2
    assert consultar(os_criacao, pedido("VIS-01", granularidade)).status == "ERRO_FERRAMENTA"


@pytest.mark.parametrize("granularidade", ["semana", "mes"])
def test_calendario_nao_afrouxa_periodo_maximo_ou_unidade(cliente, granularidade):
    consulta = pedido("VIS-01", granularidade, "2025-01-01", "2026-01-03")
    assert consultar(os_criacao, consulta).status == "ERRO_VALIDACAO"
    assert consultar(os_criacao, pedido("VIS-01", granularidade), unidade_id=True).status == "ERRO_VALIDACAO"
    cliente.assert_not_awaited()


def test_granularidade_adulterada_e_revalidada_antes_do_sql(cliente):
    consulta = pedido("VIS-01", "semana").model_copy(update={"granularidade": "MONTH'); DROP TABLE t --"})
    assert consultar(os_criacao, consulta).status == "ERRO_VALIDACAO"
    cliente.assert_not_awaited()


@pytest.mark.parametrize("granularidade", ["semana", "mes"])
def test_calendario_irrepresentavel_e_recusado_antes_de_acessar_fonte(cliente, granularidade):
    consulta = pedido("VIS-01", granularidade, "9999-12-30", "9999-12-31")
    assert consultar(os_criacao, consulta).status == "ERRO_VALIDACAO"
    cliente.assert_not_awaited()


def test_contrato_recusa_indicacao_parcial_falsa_e_recorte_fora_do_calendario():
    calendario = {"inicio": "2026-10-05", "fim": "2026-10-12"}
    with pytest.raises(ValidationError, match="parcial"):
        PeriodoSerieTemporal(calendario=calendario, consultado={"inicio": "2026-10-07", "fim": "2026-10-12"}, parcial=False)
    with pytest.raises(ValidationError, match="contido"):
        PeriodoSerieTemporal(calendario=calendario, consultado={"inicio": "2026-10-04", "fim": "2026-10-12"}, parcial=True)
    with pytest.raises(ValidationError, match="referência"):
        PontoSerieTemporal(
            data_referencia="2026-10-07", grupo={}, valor=1, qtd_registros=1,
            periodo={"calendario": calendario, "consultado": calendario, "parcial": False},
        )


def test_contrato_confronta_trecho_consultado_com_recorte_dos_metadados(cliente):
    executar_amostra(cliente, "os_criacao", [linha("qtd_os", 1, "2026-10-07")])
    resultado = consultar(os_criacao, pedido("VIS-01", "semana", "2026-10-07", "2026-10-10"))
    dados = resultado.model_dump()
    dados["dados"]["pontos"][0]["periodo"]["consultado"]["inicio"] = date(2026, 10, 6)
    with pytest.raises(ValidationError, match="recorte dos metadados"):
        ResultadoConsultaVisualizacao.model_validate(dados)


@pytest.mark.parametrize("referencia,granularidade,inicio,seguinte", [
    (date(2026, 10, 7), "dia", date(2026, 10, 7), date(2026, 10, 8)),
    (date(2026, 10, 7), "semana", date(2026, 10, 5), date(2026, 10, 12)),
    (date(2026, 10, 11), "semana", date(2026, 10, 5), date(2026, 10, 12)),
    (date(2026, 10, 12), "semana", date(2026, 10, 12), date(2026, 10, 19)),
    (date(2027, 1, 1), "semana", date(2026, 12, 28), date(2027, 1, 4)),
    (date(2026, 10, 7), "mes", date(2026, 10, 1), date(2026, 11, 1)),
    (date(2026, 12, 31), "mes", date(2026, 12, 1), date(2027, 1, 1)),
    (date(2024, 2, 29), "mes", date(2024, 2, 1), date(2024, 3, 1)),
    (date(2025, 2, 28), "mes", date(2025, 2, 1), date(2025, 3, 1)),
])
def test_calendario_respeita_segunda_feira_meses_e_anos_bissextos(referencia, granularidade, inicio, seguinte):
    assert inicio_periodo(referencia, granularidade) == inicio
    assert proximo_periodo(inicio, granularidade) == seguinte


@pytest.mark.parametrize("granularidade,expressao", [
    ("dia", "data_referencia"),
    ("semana", "TRUNC(data_referencia, 'WEEK')"),
    ("mes", "TRUNC(data_referencia, 'MONTH')"),
])
def test_granularidade_sql_vem_de_lista_fechada(granularidade, expressao):
    assert expressao_periodo_sql("data_referencia", granularidade) == expressao


@pytest.mark.parametrize("granularidade", [None, "ano", "week", "MONTH'); DROP TABLE t --"])
def test_calendario_recusa_granularidades_nao_aprovadas(granularidade):
    with pytest.raises(ValueError):
        inicio_periodo(date(2026, 10, 7), granularidade)
    with pytest.raises(ValueError):
        proximo_periodo(date(2026, 10, 5), granularidade)
    with pytest.raises(ValueError):
        expressao_periodo_sql("data_referencia", granularidade)


@pytest.mark.parametrize("granularidade", ["semana", "mes"])
def test_calendario_nao_inventa_datas_apos_ano_maximo(granularidade):
    with pytest.raises(ValueError, match="representáveis"):
        proximo_periodo(date(9999, 12, 31), granularidade)
