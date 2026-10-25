"""Testes locais do serviço de consultas Databricks, sem workspace real."""

import asyncio
import json

import httpx
import pytest

from app.core import configuracao
from app.core.clients import databricks as cliente_pool
from app.services.indicadores.gerais import databricks


def resposta_sucesso(*, linhas=None, colunas=None, proximo_chunk=None):
    result = {"data_array": linhas or [], "row_count": len(linhas or [])}
    if proximo_chunk is not None:
        result["next_chunk_index"] = proximo_chunk
    return {
        "statement_id": "stmt-teste",
        "status": {"state": "SUCCEEDED"},
        "manifest": {
            "schema": {
                "columns": [
                    {"name": nome, "type_name": "STRING"}
                    for nome in (colunas or [])
                ]
            }
        },
        "result": result,
    }


@pytest.fixture
def configurar_cliente(monkeypatch):
    monkeypatch.setattr(configuracao, "DATABRICKS_HOST", "https://workspace.example")
    monkeypatch.setattr(configuracao, "DATABRICKS_TOKEN", "token-de-teste")
    monkeypatch.setattr(configuracao, "DATABRICKS_WAREHOUSE_ID", "warehouse-teste")
    clientes = []

    def instalar(handler):
        cliente = httpx.AsyncClient(
            transport=httpx.MockTransport(handler),
        )
        clientes.append(cliente)
        monkeypatch.setattr(cliente_pool, "obter_cliente_databricks", lambda: cliente)
        return cliente

    yield instalar

    for cliente in clientes:
        asyncio.run(cliente.aclose())


def test_consulta_enviada_com_parametro_nomeado_e_retorna_linhas(configurar_cliente):
    requisicoes = []

    def responder(request):
        requisicoes.append(request)
        assert request.method == "POST"
        assert request.url.path == "/api/2.0/sql/statements"
        assert request.headers["Authorization"] == "Bearer token-de-teste"
        return httpx.Response(
            200,
            json=resposta_sucesso(linhas=[["7"]], colunas=["total"]),
        )

    configurar_cliente(responder)
    resultado = asyncio.run(databricks.executar_consulta(
        "SELECT :id AS total", {"id": 7}, tipos_parametros={"id": "INT"},
    ))

    assert resultado == [{"total": "7"}]
    corpo = json.loads(requisicoes[0].content)
    assert corpo["warehouse_id"] == "warehouse-teste"
    assert corpo["parameters"] == [{"name": "id", "value": "7", "type": "INT"}]
    assert corpo["disposition"] == "INLINE"
    assert corpo["format"] == "JSON_ARRAY"


def test_consulta_pendente_faz_polling_e_busca_chunks(configurar_cliente):
    chamadas = []

    def responder(request):
        chamadas.append((request.method, request.url.path))
        if request.method == "POST":
            return httpx.Response(200, json={
                "statement_id": "stmt-123", "status": {"state": "PENDING"},
            })
        if request.url.path == "/api/2.0/sql/statements/stmt-123":
            return httpx.Response(200, json={
                **resposta_sucesso(
                    linhas=[["primeira"]], colunas=["valor"], proximo_chunk=1,
                ),
                "statement_id": "stmt-123",
            })
        if request.url.path.endswith("/result/chunks/1"):
            return httpx.Response(200, json={
                "data_array": [["segunda"]], "row_count": 1,
            })
        return httpx.Response(404)

    configurar_cliente(responder)
    resultado = asyncio.run(databricks.executar_consulta(
        "SELECT 'valor'", tempo_limite_segundos=2,
    ))

    assert resultado == [{"valor": "primeira"}, {"valor": "segunda"}]
    assert any(caminho.endswith("/result/chunks/1") for _, caminho in chamadas)


def test_erro_sql_retorna_excecao_sem_expor_como_sucesso(configurar_cliente):
    configurar_cliente(lambda _: httpx.Response(200, json={
        "statement_id": "stmt-erro",
        "status": {
            "state": "FAILED",
            "error": {"error_code": "PARSE_SYNTAX_ERROR", "message": "SQL inválido"},
        },
    }))

    with pytest.raises(databricks.ErroConsultaDatabricks, match="PARSE_SYNTAX_ERROR"):
        asyncio.run(databricks.executar_consulta("SELECT 1"))


def test_erro_http_e_convertido_em_erro_do_cliente(configurar_cliente):
    configurar_cliente(lambda _: httpx.Response(401))

    with pytest.raises(databricks.ErroHTTPDatabricks, match="HTTP 401"):
        asyncio.run(databricks.executar_consulta("SELECT 1"))


def test_timeout_cancela_consulta_pendente(configurar_cliente):
    chamadas = []

    def responder(request):
        chamadas.append((request.method, request.url.path))
        if request.method == "POST":
            return httpx.Response(200, json={
                "statement_id": "stmt-timeout", "status": {"state": "PENDING"},
            })
        if request.url.path.endswith("/cancel"):
            return httpx.Response(200, json={})
        return httpx.Response(200, json={
            "statement_id": "stmt-timeout", "status": {"state": "RUNNING"},
        })

    configurar_cliente(responder)
    with pytest.raises(databricks.TimeoutConsultaDatabricks):
        asyncio.run(databricks.executar_consulta(
            "SELECT 1", tempo_limite_segundos=0.01,
        ))

    assert any(caminho.endswith("/cancel") for _, caminho in chamadas)


def test_sql_nao_select_ou_parametros_incompletos_sao_rejeitados(configurar_cliente):
    requisicoes = []
    configurar_cliente(lambda request: requisicoes.append(request) or httpx.Response(200))

    with pytest.raises(ValueError, match="somente consultas SELECT"):
        asyncio.run(databricks.executar_consulta("DELETE FROM tabela"))
    with pytest.raises(ValueError, match="parâmetros sem valor"):
        asyncio.run(databricks.executar_consulta("SELECT :inicio"))

    assert requisicoes == []


def test_falha_de_configuracao_indica_nomes_sem_exibir_segredos(
    monkeypatch, configurar_cliente,
):
    monkeypatch.setattr(configuracao, "DATABRICKS_HOST", None)
    monkeypatch.setattr(configuracao, "DATABRICKS_TOKEN", None)
    monkeypatch.setattr(configuracao, "DATABRICKS_WAREHOUSE_ID", None)
    configurar_cliente(lambda _: httpx.Response(200))

    with pytest.raises(databricks.ConfiguracaoDatabricksAusente) as erro:
        asyncio.run(databricks.executar_consulta("SELECT 1"))

    assert "DATABRICKS_HOST" in str(erro.value)
    assert "DATABRICKS_TOKEN" in str(erro.value)
    assert "DATABRICKS_WAREHOUSE_ID" in str(erro.value)


