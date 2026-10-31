"""27 análises: SQL controlado → grafo → API → Mongo simulado → histórico.

SQLite emula DATE/TRUNC, igualdade nula e percentile_cont. Não certifica o
dialeto Databricks, sua semântica de NaN ou o comportamento de MongoDB real.
"""

import copy
import math
import re
import sqlite3
from datetime import date, timedelta
from importlib import import_module
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from langchain.tools import ToolRuntime

from app.agents.agentsResult import VisualizacaoResultado
from app.api.dependencies.auth import obter_usuario_atual
from app.graph import executor, fluxo, nos
from app.main import app
from app.schemas import UsuarioContexto
from app.services import chat
from app.services.indicadores.gerais import databricks
from app.services.visualizacoes import ANALISES, _DOMINIOS
from app.tools.metricas_kpis import contexto as contexto_indicadores
from app.tools.visualizacoes import FERRAMENTAS_VISUALIZACOES
from app.tools.visualizacoes.contexto import MENSAGEM_BLOQUEIO_MOBILE
# Coleção reutilizada para exercer o mesmo filtro BSON e a gravação do passo 17.
from app.tests.test_visualizacoes_persistencia import mongo

juiz = import_module("app.agents.juiz")
salvar = import_module("app.memory.persistencia.salvar_mensagem")


class Percentil:
    def __init__(self):
        self.valores, self.p = [], None

    def step(self, valor, p):
        self.p = p
        if valor is not None: self.valores.append(valor)

    def finalize(self):
        if not self.valores: return None
        valores = sorted(self.valores)
        posicao = (len(valores) - 1) * self.p
        a, b = math.floor(posicao), math.ceil(posicao)
        return valores[a] + (valores[b] - valores[a]) * (posicao - a)


def amostras():
    dados = {}
    for dominio in _DOMINIOS:
        fonte = dominio.FONTE
        linhas = []
        for i, tempo in enumerate([0, 1, 2, 3, 4, 20]):
            linha = {c: "Publicado" if t == "STRING" else 1 for c, t in dominio.FILTROS.items()}
            for c in fonte.ids_textuais: linha[c] = "001"
            linha.update(unidade_id=7, unidade_nome="Autorizada", data_referencia="2026-10-02",
                         data_referencia_snapshot="2026-10-30T12:00:00+00:00", datas_prazo_validas=True)
            if fonte.id == "recorrencia": linha["data_referencia"] = f"2026-10-{i + 1:02d}"
            for chave in fonte.chave:
                if chave not in linha: linha[chave] = i + 1
            for analise in dominio.ANALISES:
                campo = analise.campo_valor
                if analise.agregacao == "COUNT": continue
                if analise.unidade_medida == "percentual": linha[campo] = [0, 100, None, 100, 0, 100][i]
                elif analise.unidade_medida == "minutos" or analise.formato_dados == "histograma": linha[campo] = tempo
                else: linha[campo] = 1
            if fonte.id == "os_atual": linha["os_prazo_vencido"] = i % 2
            if fonte.id == "ocorrencia": linha["ocorrencia_alta_prioridade"] = i % 2
            linhas.append(linha)
        estrangeira = {**linhas[0], "unidade_id": 9, "unidade_nome": "PROIBIDA"}
        if "ordem_servico_id" in estrangeira: estrangeira["ordem_servico_id"] = 900
        linhas.append(estrangeira)
        if fonte.campo_periodo:
            for id_os, dia in [(901, "2026-09-30"), (902, "2026-10-08")]:
                fora = {**linhas[0], "data_referencia": dia}
                if "ordem_servico_id" in fora: fora["ordem_servico_id"] = id_os
                linhas.append(fora)
        dados[fonte.id] = linhas
    return dados


@pytest.fixture
def integrado(monkeypatch, mongo):
    monkeypatch.setenv("LANGSMITH_TRACING", "false")
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "false")
    configuracao = {"id": "VIS-03", "granularidade": "dia", "falha": None, "perfil": "gestor"}
    dados, chamadas = amostras(), []
    usuario = UsuarioContexto(access_token="token-privado-integracao", usuario_id=10, nome_completo="Gestor",
                             email="gestor@example.com", tipo_acesso="gestor", cnpj_endereco="12345678000195")

    async def executar_sql(sql, parametros, *, tipos_parametros):
        databricks._validar_sql(sql, parametros)
        assert set(parametros) == set(tipos_parametros)
        assert parametros["unidade_id"] == 7
        assert tipos_parametros["unidade_id"] == "BIGINT"
        chamadas.append((sql, copy.deepcopy(parametros)))
        if configuracao["falha"] == "timeout": raise databricks.TimeoutConsultaDatabricks("simulado")
        if configuracao["falha"] == "truncado": raise databricks.ResultadoDatabricksTruncado("simulado")
        if configuracao["falha"] == "transporte": raise OSError("token-privado-integracao driver")
        a = ANALISES[configuracao["id"]]
        linhas = copy.deepcopy(dados[a.fonte.id])
        sql = sql.replace(a.fonte.tabela, "amostra").replace("<=>", "IS")
        sql = re.sub(r"percentile_cont\((0\.25|0\.5|0\.75)\) WITHIN GROUP \(ORDER BY valor\)",
                     r"percentil_cont(valor, \1)", sql)
        for k in ("inicio", "fim"): sql = sql.replace(f"CAST(:{k} AS DATE)", f":{k}")
        parametros = {k: v.isoformat() if type(v) is date else v for k, v in parametros.items()}
        def truncar(valor, unidade):
            dia = date.fromisoformat(valor)
            return (dia - timedelta(days=dia.weekday())).isoformat() if unidade == "WEEK" else dia.replace(day=1).isoformat()
        with sqlite3.connect(":memory:") as conexao:
            conexao.row_factory = sqlite3.Row
            conexao.create_function("isnan", 1, lambda v: int(v is not None and math.isnan(v)))
            conexao.create_function("TRUNC", 2, truncar)
            conexao.create_aggregate("percentil_cont", 2, Percentil)
            colunas = list(linhas[0])
            textuais = {c for c in colunas if isinstance(linhas[0][c], str)}
            conexao.execute("CREATE TABLE amostra (" + ", ".join(f"{c} {'TEXT' if c in textuais else 'INTEGER'}" for c in colunas) + ")")
            if configuracao["falha"] != "vazio":
                conexao.executemany(f"INSERT INTO amostra VALUES ({', '.join('?' for _ in colunas)})",
                                   [[l[c] for c in colunas] for l in linhas])
            return [dict(l) for l in conexao.execute(sql, parametros)]

    banco = AsyncMock(side_effect=executar_sql)
    unidade = AsyncMock(return_value=7)
    monkeypatch.setattr(databricks, "executar_consulta", banco)
    monkeypatch.setattr(contexto_indicadores, "obter_unidade_id", unidade)
    monkeypatch.setattr(chat, "sessao_acessivel", AsyncMock(return_value=True))
    monkeypatch.setattr(executor, "obter_documento_sessao_id", AsyncMock(return_value="documento"))
    monkeypatch.setattr(executor, "recuperar_mensagens", AsyncMock(return_value=[]))
    for nome, valor in [("obter_rascunho_solicitacao", None), ("obter_acao", None), ("obter_analise_compra", None),
                        ("obter_quantidade_anexos_pendentes", 0)]:
        monkeypatch.setattr(executor, nome, AsyncMock(return_value=valor))
    async def agente(_entrada, *, context):
        a = ANALISES[configuracao["id"]]
        tool = next(t for t in FERRAMENTAS_VISUALIZACOES if t.name == f"consultar_visualizacao_{a.fonte.id}")
        runtime = ToolRuntime(state={}, context=context, config={}, stream_writer=lambda _: None,
                              tool_call_id="consulta-integrada", store=None)
        args = {"analise_id": a.id, "runtime": runtime, "filtros": {}}
        if a.fonte.campo_periodo:
            args["periodo"] = {"inicio": "2026-10-01", "fim": "2026-10-08"}
            if a.formato_dados == "serie_temporal": args["granularidade"] = configuracao["granularidade"]
        resultado = await tool.ainvoke(args)
        sucesso = resultado["status"] in {"SUCESSO", "SUCESSO_PARCIAL"}
        return {"structured_response": VisualizacaoResultado(
            agente="visualizacao", resposta="Resultado analítico disponível." if sucesso else "Não há dados disponíveis para exibir.",
            status=resultado["status"], visualizacao={"analise_id": a.id, "consulta_id": resultado["metadados"]["consulta_id"]} if sucesso else None,
        )}
    monkeypatch.setattr(nos, "visualizacoes_gestor", SimpleNamespace(ainvoke=AsyncMock(side_effect=agente)))
    monkeypatch.setattr(nos, "visualizacoes_administrador", SimpleNamespace(ainvoke=AsyncMock(side_effect=agente)))
    async def supervisionar(_estado): return {"intencao": "visualizacao", "erro": None}
    async def emocao(_estado): return {"emocao": "NEUTRO"}
    monkeypatch.setattr(fluxo, "supervisionar", supervisionar)
    monkeypatch.setattr(fluxo, "classificar_emocao", emocao)
    monkeypatch.setattr(nos, "proteger_entrada", lambda _: {"bloqueado": False})
    monkeypatch.setattr(executor, "grafo", fluxo.construir_grafo())
    julgar = AsyncMock(return_value={"model": "roteirizado", "answers": {
        "veredito": {"type": "choice", "choice": "aprovado", "confidence": 0.95},
        "motivo": {"type": "choice", "choice": "nenhum", "confidence": 0.95},
        **{k: {"type": "noul", "noul": 0.05} for k in (
            "afirmacao_sem_suporte", "correcao_textual", "risco_grave", "visualizacao_incompativel",
        )},
    }})
    monkeypatch.setattr(juiz, "consultar_jev", julgar)
    app.dependency_overrides[obter_usuario_atual] = lambda: usuario.model_copy(update={"tipo_acesso": configuracao["perfil"]})
    try:
        yield SimpleNamespace(config=configuracao, dados=dados, banco=banco, unidade=unidade, mongo=mongo,
                              cliente=TestClient(app), chamadas=chamadas, julgar=julgar,
                              agente=nos.visualizacoes_gestor.ainvoke,
                              agente_administrador=nos.visualizacoes_administrador.ainvoke)
    finally: app.dependency_overrides.clear()


def chamar(c, identificador, granularidade="dia", plataforma="web"):
    c.config.update(id=identificador, granularidade=granularidade)
    return c.cliente.post("/api/v1/chat", json={"mensagem": f"Consultar {identificador}",
                                              "plataforma": plataforma, "thread_id": "sessao"})


CASOS = [(i, "dia") for i in sorted(ANALISES)] + [
    (a.id, g) for a in ANALISES.values() if a.formato_dados == "serie_temporal" for g in ("semana", "mes")
]


@pytest.mark.parametrize("identificador", ["VIS-01", "VIS-03", "VIS-09", "VIS-12", "VIS-15", "VIS-22"])
@pytest.mark.parametrize("perfil", ["gestor", "administrador"])
def test_mobile_bloqueia_antes_do_agente_e_das_consultas(integrado, identificador, perfil):
    c = integrado
    c.config["perfil"] = perfil
    resposta = chamar(c, identificador, plataforma="mobile")
    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["resposta"] == MENSAGEM_BLOQUEIO_MOBILE
    assert resposta.json()["intencao"] == "visualizacao"
    assert "visualizacao" not in resposta.json()
    c.agente.assert_not_awaited()
    c.agente_administrador.assert_not_awaited()
    c.unidade.assert_not_awaited()
    c.banco.assert_not_awaited()
    c.julgar.assert_not_awaited()
    mensagem = c.mongo.doc["mensagens"][-1]
    assert mensagem["role"] == "assistant" and mensagem["content"] == MENSAGEM_BLOQUEIO_MOBILE
    assert "visualizacao" not in mensagem


def test_mobile_continua_usando_outros_especialistas(integrado, monkeypatch):
    c = integrado
    monkeypatch.setattr(fluxo, "supervisionar", AsyncMock(return_value={"intencao": "faq", "erro": None}))
    faq = AsyncMock(return_value={"resposta_especialista": "Você pode acompanhar suas solicitações no aplicativo.",
                                 "erro": None})
    monkeypatch.setattr(fluxo, "executar_faq", faq)
    monkeypatch.setattr(executor, "grafo", fluxo.construir_grafo())
    resposta = chamar(c, "VIS-03", plataforma="mobile")
    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["intencao"] == "faq"
    assert resposta.json()["resposta"] == "Você pode acompanhar suas solicitações no aplicativo."
    faq.assert_awaited_once()
    c.julgar.assert_awaited_once()
    c.agente.assert_not_awaited()
    c.banco.assert_not_awaited()


def test_alternar_plataforma_na_mesma_conversa_nao_reutiliza_grafico(integrado):
    c = integrado
    assert "visualizacao" in chamar(c, "VIS-03").json()
    c.agente.reset_mock()
    c.unidade.reset_mock()
    c.banco.reset_mock()
    c.julgar.reset_mock()
    mobile = chamar(c, "VIS-03", plataforma="mobile")
    assert mobile.status_code == 200
    assert mobile.json()["resposta"] == MENSAGEM_BLOQUEIO_MOBILE
    assert "visualizacao" not in mobile.json()
    c.agente.assert_not_awaited()
    c.unidade.assert_not_awaited()
    c.banco.assert_not_awaited()
    c.julgar.assert_not_awaited()
    web = chamar(c, "VIS-03")
    assert web.status_code == 200 and "visualizacao" in web.json()
    c.agente.assert_awaited_once()
    c.banco.assert_awaited_once()


@pytest.mark.parametrize("identificador,granularidade", CASOS)
@pytest.mark.parametrize("perfil", ["gestor", "administrador"])
def test_27_analises_e_calendarios_ate_o_historico(integrado, identificador, granularidade, perfil):
    c = integrado
    c.config["perfil"] = perfil
    resposta = chamar(c, identificador, granularidade)
    assert resposta.status_code == 200, resposta.text
    assert "visualizacao" in resposta.json(), resposta.text
    grafico = resposta.json()["visualizacao"]
    a = ANALISES[identificador]
    assert grafico["dados"]["tipo"] == a.formato_dados
    assert grafico["metadados"]["analise_id"] == identificador
    assert grafico["metadados"]["unidade_id"] == 7
    assert "PROIBIDA" not in resposta.text and "token-privado-integracao" not in resposta.text
    assert grafico == c.mongo.doc["mensagens"][-1]["visualizacao"]
    recuperado = c.cliente.post("/api/v1/sessoes/conversa", json={"session_id": "sessao"})
    assert recuperado.status_code == 200, recuperado.text
    assert grafico == recuperado.json()["conversa"]["mensagens"][-1]["visualizacao"]
    assert c.banco.await_count == c.unidade.await_count == 1
    if a.formato_dados == "boxplot":
        g = grafico["dados"]["grupos"][0]
        assert (g["q1"], g["mediana"], g["q3"]) == (1.25, 2.5, 3.75)
        assert (g["bigode_inferior"], g["bigode_superior"]) == (0, 4)
        assert g["valores_extremos"] == [20] and g["qtd_registros"] == 6
    elif a.formato_dados == "histograma":
        assert grafico["dados"]["qtd_registros"] == 6
        assert sum(b["frequencia"] for b in grafico["dados"]["intervalos"]) == 6
        assert len(grafico["dados"]["intervalos"]) == 10
        assert [b["frequencia"] for b in grafico["dados"]["intervalos"]] == [2, 2, 1, 0, 0, 0, 0, 0, 0, 1]
        assert grafico["dados"]["intervalos"][-1]["inclui_superior"]
    else:
        pontos = grafico["dados"]["pontos"]
        if a.agregacao == "AVG":
            if identificador == "VIS-14" and granularidade == "dia":
                assert [p["valor"] for p in pontos] == [0, 100, None, 100, 0, 100, None]
            elif identificador == "VIS-14" and granularidade == "semana":
                assert [p["valor"] for p in pontos] == pytest.approx([200 / 3, 50])
            else:
                assert [p["valor"] for p in pontos if p["qtd_registros"]] == [5 if identificador == "VIS-21" else 60]
            if a.unidade_medida == "percentual":
                assert grafico["metadados"]["escala_percentual"] == 100
                assert grafico["metadados"]["base_calculo"]["qtd_registros_elegiveis"] == 5
                assert grafico["status"] == "SUCESSO_PARCIAL"
        else:
            assert sum(p["valor"] for p in pontos) == (3 if identificador in {"VIS-22", "VIS-27"} else 6)
        if a.formato_dados == "serie_temporal":
            assert grafico["metadados"]["granularidade"] == granularidade
            assert len(pontos) == {"dia": 7, "semana": 2, "mes": 1}[granularidade]
            if granularidade != "dia": assert pontos[0]["periodo"]["parcial"]


@pytest.mark.parametrize("identificador", ["VIS-02", "VIS-07", "VIS-15", "VIS-20"])
@pytest.mark.parametrize("falha", ["vazio", "timeout", "truncado", "transporte"])
def test_falhas_de_conclusao_nao_publicam_grafico(integrado, identificador, falha):
    c = integrado
    c.config["falha"] = falha
    resposta = chamar(c, identificador)
    assert resposta.status_code == 200, resposta.text
    assert "visualizacao" not in resposta.json()
    assert "visualizacao" not in c.mongo.doc["mensagens"][-1]
    assert "token-privado-integracao" not in resposta.text


@pytest.mark.parametrize("perfil", ["tecnico", "solicitante"])
def test_perfil_sem_acesso_nao_executa_consulta(integrado, perfil):
    integrado.config["perfil"] = perfil
    resposta = chamar(integrado, "VIS-03")
    assert resposta.status_code == 200 and "visualizacao" not in resposta.json()
    integrado.banco.assert_not_awaited()
    integrado.unidade.assert_not_awaited()


@pytest.mark.parametrize("identificador", ["VIS-06", "VIS-07"])
def test_histograma_zero_negativos_e_nulos_ate_a_api(integrado, identificador):
    c = integrado
    a = ANALISES[identificador]
    for linha, valor in zip(c.dados[a.fonte.id][:6], [-1, None, 0, 0, 0, 0]): linha[a.campo_valor] = valor
    r = chamar(c, identificador)
    g = r.json()["visualizacao"]
    assert g["status"] == "SUCESSO_PARCIAL"
    assert g["metadados"]["base_calculo"] == {
        "qtd_registros_total": 6, "qtd_registros_elegiveis": 4, "qtd_tempos_negativos_excluidos": 1,
    }
    assert g["dados"]["intervalos"] == [{"inferior": 0, "superior": 0, "frequencia": 4, "inclui_superior": True}]
    assert g == c.mongo.doc["mensagens"][-1]["visualizacao"]


@pytest.mark.parametrize("identificador", ["VIS-15", "VIS-16", "VIS-17"])
def test_boxplot_pequeno_publica_resumo_com_cobertura(integrado, identificador):
    c = integrado
    a = ANALISES[identificador]
    for linha, valor in zip(c.dados[a.fonte.id][:6], [0, 1, 2, 3, None, -1]): linha[a.campo_valor] = valor
    g = chamar(c, identificador).json()["visualizacao"]
    grupo = g["dados"]["grupos"][0]
    assert grupo["tipo"] == "resumo" and grupo["qtd_registros"] == 4
    assert (grupo["minimo"], grupo["maximo"], grupo["media"], grupo["mediana"]) == (0, 3, 1.5, 1.5)
    assert grupo["base_calculo"]["qtd_tempos_negativos_excluidos"] == 1
    assert g["status"] == "SUCESSO_PARCIAL"
    assert g == c.mongo.doc["mensagens"][-1]["visualizacao"]


def test_extremos_limitados_preservam_estatisticas_e_omissoes(integrado):
    c = integrado
    base = c.dados["os_conclusao"][0]
    c.dados["os_conclusao"] = [{**base, "ordem_servico_id": i + 1, "tempo_resolucao_minutos": v}
                               for i, v in enumerate([0] * 200 + list(range(1, 81)))]
    g = chamar(c, "VIS-15").json()["visualizacao"]
    grupo = g["dados"]["grupos"][0]
    assert grupo["qtd_registros"] == 280 and grupo["q3"] == 10.25
    assert grupo["qtd_extremos_total"] == 55 and grupo["qtd_extremos_omitidos"] == 5
    assert grupo["valores_extremos"] == list(range(80, 30, -1))
    assert g["status"] == "SUCESSO_PARCIAL" and g["avisos"]


def test_sla_agrega_populacao_e_filtra_datas_invalidas(integrado):
    c = integrado
    base = c.dados["os_conclusao"][0]
    c.dados["os_conclusao"].extend([
        {**base, "ordem_servico_id": 20, "data_referencia": "2026-10-03", "conclusao_prazo_pct_item": 0},
        {**base, "ordem_servico_id": 21, "datas_prazo_validas": False, "conclusao_prazo_pct_item": 100},
    ])
    g = chamar(c, "VIS-20", "semana").json()["visualizacao"]
    pontos = [p for p in g["dados"]["pontos"] if p["qtd_registros"]]
    assert [p["valor"] for p in pontos] == [50]  # média de 6 itens, não média das médias 60 e 0
    assert g["metadados"]["base_calculo"]["qtd_registros_total"] == 8
    assert g["metadados"]["base_calculo"]["qtd_registros_elegiveis"] == 6


@pytest.mark.parametrize("identificador", ["VIS-14", "VIS-20", "VIS-23"])
def test_ausencia_de_base_nao_e_convertida_em_zero(integrado, identificador):
    c = integrado
    a = ANALISES[identificador]
    for l in c.dados[a.fonte.id]: l[a.campo_valor] = None
    r = chamar(c, identificador)
    assert r.status_code == 200 and "visualizacao" not in r.json()
    consulta = c.julgar.await_args.args[0]["visualizacao"]["consultas"][0]
    assert consulta["status"] == "SEM_BASE_CALCULO"
    assert consulta["metadados"]["base_calculo"]["qtd_registros_elegiveis"] == 0


def test_vinculo_ausente_impede_warehouse(integrado):
    c = integrado
    c.unidade.return_value = None
    r = chamar(c, "VIS-03")
    assert r.status_code == 200 and "visualizacao" not in r.json()
    c.banco.assert_not_awaited()


def test_metricas_medem_sem_identificadores_ou_conteudo(integrado):
    from prometheus_client import REGISTRY, generate_latest
    c = integrado
    nome = "fixa_visualization_service_calls_total"
    labels = {"analysis": "VIS-03", "outcome": "SUCESSO"}
    contador = REGISTRY.get_sample_value(nome, labels) or 0
    bytes_antes = REGISTRY.get_sample_value("fixa_visualization_json_bytes_count", {"stage": "publico"}) or 0
    resposta = chamar(c, "VIS-03")
    assert resposta.status_code == 200
    assert REGISTRY.get_sample_value(nome, labels) == contador + 1
    assert REGISTRY.get_sample_value("fixa_visualization_json_bytes_count", {"stage": "publico"}) == bytes_antes + 1
    familias = [f for f in REGISTRY.collect() if f.name.startswith("fixa_visualization_")]
    assert familias
    for familia in familias:
        for amostra in familia.samples:
            assert set(amostra.labels) <= {"analysis", "outcome", "stage", "le"}
            if "analysis" in amostra.labels: assert amostra.labels["analysis"] in set(ANALISES) | {"desconhecida"}
            if "stage" in amostra.labels: assert amostra.labels["stage"] in {"tool", "juiz", "revisor", "publico"}
    exposicao = generate_latest().decode()
    assert "token-privado-integracao" not in exposicao and "PROIBIDA" not in exposicao


def test_analise_desconhecida_nao_cria_rotulo_com_entrada_recebida(integrado):
    import asyncio
    from prometheus_client import generate_latest
    from app.schemas.visualizacao import ConsultaVisualizacaoSnapshot
    from app.services.visualizacoes import os_atual
    consulta = ConsultaVisualizacaoSnapshot.model_construct(analise_id="identificador-privado-123", filtros={})
    resultado = asyncio.run(os_atual.consultar(consulta, unidade_id=7))
    assert resultado.status == "ERRO_VALIDACAO"
    integrado.banco.assert_not_awaited()
    exposicao = generate_latest().decode()
    assert 'analysis="desconhecida"' in exposicao and "identificador-privado-123" not in exposicao
