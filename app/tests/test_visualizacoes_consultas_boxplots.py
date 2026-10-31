"""Boxplots completos, resumos, cobertura e seleção determinística de extremos."""

import asyncio
from datetime import date
import math
import re
import sqlite3
from unittest.mock import AsyncMock

import pytest

from app.schemas.visualizacao import ConsultaVisualizacaoPeriodo, ResultadoConsultaVisualizacao
from app.services.indicadores.gerais import databricks
from app.services.visualizacoes import os_conclusao, os_criacao


CASOS = [
    (os_conclusao, "VIS-15", "os_conclusao", "tempo_resolucao_minutos"),
    (os_criacao, "VIS-16", "os_criacao", "tempo_pausado_minutos"),
    (os_criacao, "VIS-17", "os_criacao", "tempo_espera_minutos"),
]


@pytest.fixture(autouse=True)
def cliente(monkeypatch):
    executar = AsyncMock()
    monkeypatch.setattr(databricks, "executar_consulta", executar)
    return executar


def pedido(analise_id, filtros=None):
    return ConsultaVisualizacaoPeriodo(
        analise_id=analise_id, periodo={"inicio": "2026-10-01", "fim": "2026-10-04"},
        filtros=filtros or {},
    )


def consultar(servico, analise_id, *, unidade_id=7, filtros=None):
    return asyncio.run(servico.consultar(pedido(analise_id, filtros), unidade_id=unidade_id))


def amostra(campo, valores, *, inicio_id=1, **grupo):
    return [
        {"unidade_id": 7, "unidade_nome": "Unidade", "categoria_problema_id": 1,
         "categoria_problema": "Categoria", "tipo_local": "Sala", **grupo,
         "ordem_servico_id": inicio_id + i, "data_referencia": "2026-10-02", campo: valor}
        for i, valor in enumerate(valores)
    ]


class PercentilContinuo:
    def __init__(self):
        self.valores = []
        self.percentil = None

    def step(self, valor, percentil):
        self.percentil = percentil
        if valor is not None:
            self.valores.append(valor)

    def finalize(self):
        if not self.valores:
            return None
        valores = sorted(self.valores)
        posicao = (len(valores) - 1) * self.percentil
        inferior, superior = math.floor(posicao), math.ceil(posicao)
        return valores[inferior] + (valores[superior] - valores[inferior]) * (posicao - inferior)


def executar_amostra(cliente, fonte, linhas, transformar=None):
    """Executa CTEs, joins e ranks reais; emula o percentil do dialeto Databricks.

    Não certifica o dialeto do warehouse nem a semântica especial de NaN.
    """
    async def executar(sql, parametros, *, tipos_parametros):
        databricks._validar_sql(sql, parametros)
        assert set(parametros) == set(tipos_parametros)
        assert f"FROM workspace.fixa_pipeline.gold_dashboard_{fonte}" in sql
        assert "LIMIT " not in sql and "COLLECT_LIST" not in sql.upper()
        sql = sql.replace(f"workspace.fixa_pipeline.gold_dashboard_{fonte}", "amostra").replace("<=>", "IS")
        sql = re.sub(
            r"percentile_cont\((0\.25|0\.5|0\.75)\) WITHIN GROUP \(ORDER BY valor\)",
            r"percentil_cont(valor, \1)", sql,
        )
        for marcador in ("inicio", "fim"):
            sql = sql.replace(f"CAST(:{marcador} AS DATE)", f":{marcador}")
        parametros = {k: v.isoformat() if type(v) is date else v for k, v in parametros.items()}
        with sqlite3.connect(":memory:") as conexao:
            conexao.row_factory = sqlite3.Row
            conexao.create_function("isnan", 1, lambda v: int(v is not None and math.isnan(v)))
            conexao.create_aggregate("percentil_cont", 2, PercentilContinuo)
            colunas = list(linhas[0])
            conexao.execute(f"CREATE TABLE amostra ({', '.join(colunas)})")
            conexao.executemany(
                f"INSERT INTO amostra VALUES ({', '.join('?' for _ in colunas)})",
                [tuple(linha[c] for c in colunas) for linha in linhas],
            )
            resultado = [dict(linha) for linha in conexao.execute(sql, parametros)]
        cliente.linhas_sql = resultado
        return transformar(resultado) if transformar else resultado
    cliente.side_effect = executar


@pytest.mark.parametrize("servico,analise_id,fonte,campo", CASOS)
def test_tres_boxplots_usam_toda_populacao_e_quartis_interpolados(cliente, servico, analise_id, fonte, campo):
    executar_amostra(cliente, fonte, amostra(campo, [0, 1, 2, 3, 4, 20]))
    resultado = consultar(servico, analise_id)
    assert resultado.status == "SUCESSO"
    grupo = resultado.dados.grupos[0]
    assert grupo.tipo == "boxplot" and grupo.qtd_registros == 6
    assert (grupo.q1, grupo.mediana, grupo.q3) == (1.25, 2.5, 3.75)
    assert (grupo.limite_inferior, grupo.limite_superior) == (-2.5, 7.5)
    assert (grupo.bigode_inferior, grupo.bigode_superior) == (0, 4)
    assert grupo.valores_extremos == [20] and grupo.qtd_extremos_total == 1
    assert grupo.base_calculo.qtd_registros_total == 6
    assert resultado.metadados.qtd_registros_considerados == 6
    assert resultado.metadados.campo_valor == campo
    assert ResultadoConsultaVisualizacao.model_validate_json(resultado.model_dump_json()) == resultado


@pytest.mark.parametrize("servico,analise_id,fonte,campo", CASOS)
@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_grupos_pequenos_usam_resumo_integrado(cliente, servico, analise_id, fonte, campo, n):
    executar_amostra(cliente, fonte, amostra(campo, list(range(n))))
    resultado = consultar(servico, analise_id)
    grupo = resultado.dados.grupos[0]
    assert grupo.tipo == "resumo" and grupo.qtd_registros == n
    assert (grupo.minimo, grupo.maximo, grupo.media, grupo.mediana) == (0, n - 1, (n - 1) / 2, (n - 1) / 2)
    assert grupo.base_calculo.qtd_registros_elegiveis == n
    assert not hasattr(grupo, "q1")


@pytest.mark.parametrize("valores,extremos", [([0] * 5, []), ([0, 0, 0, 0, 100], [100])])
def test_iqr_zero_preserva_caixa_sem_dispersao_inventada(cliente, valores, extremos):
    executar_amostra(cliente, "os_criacao", amostra("tempo_pausado_minutos", valores))
    grupo = consultar(os_criacao, "VIS-16").dados.grupos[0]
    assert grupo.q1 == grupo.mediana == grupo.q3 == grupo.bigode_inferior == grupo.bigode_superior == 0
    assert grupo.valores_extremos == extremos


def test_observacoes_exatamente_nos_limites_pertencem_aos_bigodes(cliente):
    executar_amostra(cliente, "os_criacao", amostra("tempo_pausado_minutos", [0, 3, 3, 4, 5, 5, 8]))
    grupo = consultar(os_criacao, "VIS-16").dados.grupos[0]
    assert (grupo.limite_inferior, grupo.limite_superior) == (0, 8)
    assert (grupo.bigode_inferior, grupo.bigode_superior) == (0, 8)
    assert grupo.qtd_extremos_total == 0


def test_grupos_mistos_resumos_nulos_e_sem_base_nao_desaparecem(cliente):
    campo = "tempo_pausado_minutos"
    linhas = amostra(campo, range(5), categoria_problema_id=1)
    linhas += amostra(campo, [10, 20, 30, 40], inicio_id=10, categoria_problema_id=2)
    linhas += amostra(campo, [None, -2], inicio_id=20, categoria_problema_id=3)
    linhas += amostra(campo, [0], inicio_id=30, categoria_problema_id=None, categoria_problema=None)
    executar_amostra(cliente, "os_criacao", linhas)
    resultado = consultar(os_criacao, "VIS-16")
    assert resultado.status == "SUCESSO_PARCIAL"
    assert [g.tipo for g in resultado.dados.grupos] == ["resumo", "boxplot", "resumo", "sem_base"]
    assert resultado.dados.grupos[0].grupo == {"categoria_problema_id": None, "categoria_problema": None}
    sem_base = resultado.dados.grupos[-1]
    assert sem_base.qtd_registros == 0 and not hasattr(sem_base, "mediana")
    assert sem_base.base_calculo.qtd_registros_total == 2
    assert sem_base.base_calculo.qtd_tempos_negativos_excluidos == 1
    assert resultado.metadados.base_calculo.qtd_registros_total == 12
    assert resultado.metadados.qtd_registros_considerados == 10
    assert ResultadoConsultaVisualizacao.model_validate_json(resultado.model_dump_json()) == resultado


@pytest.mark.parametrize("servico,analise_id,fonte,campo", CASOS)
def test_negativos_e_nulos_excluidos_zero_preservado(cliente, servico, analise_id, fonte, campo):
    executar_amostra(cliente, fonte, amostra(campo, [-2, None, 0, 1, 2, 3, 4]))
    resultado = consultar(servico, analise_id)
    assert resultado.status == "SUCESSO_PARCIAL"
    grupo = resultado.dados.grupos[0]
    assert grupo.tipo == "boxplot" and grupo.qtd_registros == 5 and grupo.minimo == 0
    assert grupo.base_calculo.qtd_tempos_negativos_excluidos == 1
    assert resultado.metadados.base_calculo.qtd_registros_total == 7
    assert any("negativos excluídos: 1" in a for a in resultado.avisos)


@pytest.mark.parametrize("servico,analise_id,fonte,campo", CASOS)
def test_fonte_vazia_e_fonte_sem_elegiveis_diferem(cliente, servico, analise_id, fonte, campo):
    executar_amostra(cliente, fonte, amostra(campo, [1], unidade_id=8))
    vazio = consultar(servico, analise_id)
    assert vazio.status == "SEM_RESULTADO" and vazio.dados is None
    assert vazio.metadados.base_calculo.qtd_registros_total == 0
    executar_amostra(cliente, fonte, amostra(campo, [None, -1]))
    sem_base = consultar(servico, analise_id)
    assert sem_base.status == "SEM_BASE_CALCULO" and sem_base.dados is None
    assert sem_base.metadados.base_calculo.qtd_tempos_negativos_excluidos == 1


def test_limite_por_grupo_prioriza_afastamento_sem_recalcular_quartis(cliente):
    executar_amostra(cliente, "os_criacao", amostra("tempo_pausado_minutos", [1] * 200 + list(range(100, 160))))
    resultado = consultar(os_criacao, "VIS-16")
    grupo = resultado.dados.grupos[0]
    assert resultado.status == "SUCESSO_PARCIAL"
    assert grupo.qtd_registros == 260 and grupo.q1 == grupo.q3 == 1
    assert grupo.valores_extremos == list(range(159, 109, -1))
    assert grupo.qtd_extremos_total == 60 and grupo.qtd_extremos_omitidos == 10


def test_limite_global_mantem_grupos_com_todos_os_extremos_omitidos(cliente):
    linhas = []
    for i in range(1, 13):
        linhas += amostra("tempo_pausado_minutos", [1] * 200 + [100 + i] * 60,
                          inicio_id=i * 1000, categoria_problema_id=i)
    executar_amostra(cliente, "os_criacao", linhas)
    resultado = consultar(os_criacao, "VIS-16")
    assert resultado.status == "SUCESSO_PARCIAL" and len(resultado.dados.grupos) == 12
    grupos = resultado.dados.grupos
    assert sum(len(g.valores_extremos) for g in grupos) == 500
    assert sum(g.qtd_extremos_total for g in grupos) == 720
    assert sum(g.qtd_extremos_omitidos for g in grupos) == 220
    assert all(not g.valores_extremos and g.qtd_extremos_omitidos == 60 for g in grupos[:2])
    assert all(len(g.valores_extremos) == 50 for g in grupos[2:])
    assert resultado.metadados.qtd_registros_considerados == 3120
    assert len(cliente.linhas_sql) == 512


def test_extremos_inferiores_e_superiores_compartilham_prioridade_por_afastamento(cliente):
    valores = [50] * 200 + list(range(60))
    executar_amostra(cliente, "os_criacao", amostra("tempo_pausado_minutos", valores))
    grupo = consultar(os_criacao, "VIS-16").dados.grupos[0]
    assert grupo.q1 == grupo.q3 == 50
    esperados = sorted((v for v in range(60) if v != 50), key=lambda v: (-abs(v - 50), v))[:50]
    assert grupo.valores_extremos == esperados
    assert grupo.qtd_extremos_total == 59 and grupo.qtd_extremos_omitidos == 9


def test_empates_sao_estaveis_e_extremos_iguais_de_os_distintas_nao_sao_deduplicados(cliente):
    linhas = amostra("tempo_pausado_minutos", [1] * 200 + [100] * 60, inicio_id=9007199254740993)
    executar_amostra(cliente, "os_criacao", linhas)
    primeiro = consultar(os_criacao, "VIS-16")
    chaves_primeiro = [l["chave_os"] for l in cliente.linhas_sql if l["tipo_linha"] == 1]
    executar_amostra(cliente, "os_criacao", list(reversed(linhas)))
    segundo = consultar(os_criacao, "VIS-16")
    chaves_segundo = [l["chave_os"] for l in cliente.linhas_sql if l["tipo_linha"] == 1]
    assert primeiro.dados == segundo.dados
    assert primeiro.dados.grupos[0].valores_extremos == [100] * 50
    assert chaves_primeiro == chaves_segundo == list(range(9007199254741193, 9007199254741243))


@pytest.mark.parametrize("quantidade,status", [(50, "SUCESSO"), (51, "ERRO_VALIDACAO")])
def test_limite_de_grupos_nao_corta_grupos_silenciosamente(cliente, quantidade, status):
    linhas = []
    for i in range(quantidade):
        linhas += amostra("tempo_pausado_minutos", [0] * 5, inicio_id=i * 10, categoria_problema_id=i)
    executar_amostra(cliente, "os_criacao", linhas)
    resultado = consultar(os_criacao, "VIS-16")
    assert resultado.status == status
    assert (resultado.dados is not None) == (quantidade == 50)


def test_periodo_unidade_e_filtros_precedem_todas_as_estatisticas(cliente):
    linhas = amostra("tempo_resolucao_minutos", range(5))
    linhas += amostra("tempo_resolucao_minutos", [100], inicio_id=10, unidade_id=8)
    fora = amostra("tempo_resolucao_minutos", [100], inicio_id=20)
    fora[0]["data_referencia"] = "2026-10-04"
    linhas += fora
    linhas += amostra("tempo_resolucao_minutos", [100], inicio_id=30, tipo_local="Outro")
    executar_amostra(cliente, "os_conclusao", linhas)
    resultado = consultar(os_conclusao, "VIS-15", filtros={"tipo_local": ["Sala", "Lab"]})
    grupo = resultado.dados.grupos[0]
    assert grupo.grupo == {"unidade_id": 7, "unidade_nome": "Unidade"}
    assert grupo.qtd_registros == 5 and grupo.maximo == 4


@pytest.mark.parametrize("valor", [float("inf"), -float("inf")])
def test_nao_finitos_nao_sao_descartados_como_negativos(cliente, valor):
    executar_amostra(cliente, "os_criacao", amostra("tempo_pausado_minutos", [1] * 5 + [valor]))
    assert consultar(os_criacao, "VIS-16").status == "ERRO_FERRAMENTA"


@pytest.mark.parametrize("chave", [None, 1])
def test_chaves_nulas_ou_duplicadas_nao_alteram_grain_silenciosamente(cliente, chave):
    linhas = amostra("tempo_pausado_minutos", range(5))
    linhas[-1]["ordem_servico_id"] = chave
    executar_amostra(cliente, "os_criacao", linhas)
    assert consultar(os_criacao, "VIS-16").status == "ERRO_FERRAMENTA"


@pytest.mark.parametrize("campo,valor", [
    ("qtd_grupos", "1.5"), ("qtd_registros_invalidos", 1), ("qtd_registros_total", 1),
    ("qtd_chaves_invalidas", 1), ("q1", "NaN"), ("limite_superior", 123),
    ("qtd_extremos_total", 0), ("bigode_inferior", None),
])
def test_estatisticas_incompativeis_nao_liberam_grafico(cliente, campo, valor):
    def alterar(linhas):
        linhas[0][campo] = valor
        return linhas
    executar_amostra(cliente, "os_criacao", amostra("tempo_pausado_minutos", [0, 1, 2, 3, 4, 20]), alterar)
    assert consultar(os_criacao, "VIS-16").status == "ERRO_FERRAMENTA"


@pytest.mark.parametrize("mudanca", ["remover_extremo", "duplicar_extremo", "afastamento", "ordem_global", "grupo_estranho"])
def test_selecao_incompleta_ou_incoerente_de_extremos_e_erro(cliente, mudanca):
    def alterar(linhas):
        if mudanca == "remover_extremo":
            return linhas[:1]
        if mudanca == "duplicar_extremo":
            return linhas + [dict(linhas[-1])]
        linhas[-1][{"afastamento": "afastamento", "ordem_global": "ordem_global",
                     "grupo_estranho": "grupo_indice"}[mudanca]] = 999
        return linhas
    executar_amostra(cliente, "os_criacao", amostra("tempo_pausado_minutos", [0, 1, 2, 3, 4, 20]), alterar)
    assert consultar(os_criacao, "VIS-16").status == "ERRO_FERRAMENTA"


def test_unidade_retornada_diferente_do_escopo_e_erro(cliente):
    def alterar(linhas):
        linhas[0]["unidade_id"] = 8
        return linhas
    executar_amostra(cliente, "os_conclusao", amostra("tempo_resolucao_minutos", range(5)), alterar)
    assert consultar(os_conclusao, "VIS-15").status == "ERRO_FERRAMENTA"


@pytest.mark.parametrize("servico,analise_id,fonte,campo", CASOS)
def test_unidade_invalida_nao_consulta(cliente, servico, analise_id, fonte, campo):
    assert consultar(servico, analise_id, unidade_id=True).status == "ERRO_VALIDACAO"
    cliente.assert_not_awaited()


@pytest.mark.parametrize("filtros", [{"unidade_id": 8}, {"instituicao_id": 8}, {"sql": "SELECT 1"}])
def test_comparacao_entre_unidades_nao_e_liberada_por_filtro(cliente, filtros):
    assert consultar(os_conclusao, "VIS-15", filtros=filtros).status == "ERRO_VALIDACAO"
    cliente.assert_not_awaited()


@pytest.mark.parametrize("erro,status", [
    (databricks.TimeoutConsultaDatabricks("segredo"), "TIMEOUT"),
    (databricks.ResultadoDatabricksTruncado("segredo"), "RESULTADO_TRUNCADO"),
    (RuntimeError("segredo"), "ERRO_FERRAMENTA"),
])
def test_falhas_nao_liberam_estatisticas_parciais(cliente, erro, status):
    cliente.side_effect = erro
    resultado = consultar(os_criacao, "VIS-16")
    assert resultado.status == status and resultado.dados is None
    assert "segredo" not in resultado.model_dump_json()
