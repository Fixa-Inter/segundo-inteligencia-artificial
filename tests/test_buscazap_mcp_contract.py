"""Four live contract checks for the BuscaZap MCP endpoint.

Run explicitly: python -m pytest tests/test_buscazap_mcp_contract.py -q
"""

import os

import httpx
import pytest


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_BUSCAZAP_LIVE_TESTS") != "1",
    reason="Os testes de contrato usam a cota real do BuscaZap; execute explicitamente.",
)


URL = "https://www.buscazap.com.br/mcp"


def rpc(method: str, params: dict | None = None) -> dict:
    body = {"jsonrpc": "2.0", "id": 1, "method": method}
    if params is not None:
        body["params"] = params
    with httpx.Client(timeout=35, follow_redirects=False) as client:
        response = client.post(URL, json=body, headers={"Accept": "application/json"})
    response.raise_for_status()
    payload = response.json()
    assert payload.get("jsonrpc") == "2.0"
    assert "error" not in payload, payload.get("error")
    return payload["result"]


def test_discover_search_tool():
    result = rpc("tools/list")
    tools = {tool["name"]: tool for tool in result["tools"]}
    assert "buscar_produtos_por_contexto" in tools
    schema = tools["buscar_produtos_por_contexto"]["inputSchema"]
    assert "context" in schema["required"]
    assert {"context", "limit", "recomendar"} <= set(schema["properties"])


def test_search_with_full_technical_summary():
    context = (
        "Item: furadeira de impacto. Aplicação: perfuração de alvenaria. "
        "Requisitos obrigatórios: 220 V, mandril de 13 mm, alimentação por cabo. "
        "Quantidade: 1 unidade. Orçamento: até R$ 500. "
        "Preferências: Bosch ou Makita. Exclusões: ferramentas a bateria."
    )
    result = rpc("tools/call", {"name": "buscar_produtos_por_contexto", "arguments": {
        "context": context, "limit": 5, "recomendar": True,
    }})
    assert result.get("isError") is False, result
    products = result["structuredContent"]["products"]
    assert isinstance(products, list)
    assert len(products) <= 5
    for product in products:
        assert isinstance(product.get("short_description"), str)
        assert isinstance(product.get("store_name"), str)
        assert isinstance(product.get("url"), str)


def test_search_with_priority_fields_only():
    context = (
        "Item: broca para concreto. Requisitos obrigatórios: diâmetro 8 mm, "
        "encaixe SDS Plus. Quantidade: 2 unidades. Os demais campos não foram informados."
    )
    result = rpc("tools/call", {"name": "buscar_produtos_por_contexto", "arguments": {
        "context": context, "limit": 5, "recomendar": True,
    }})
    assert result.get("isError") is False, result
    assert isinstance(result["structuredContent"]["products"], list)


def test_list_store_coverage():
    result = rpc("tools/call", {"name": "listar_lojas", "arguments": {}})
    assert result.get("isError") is False, result
    assert result.get("structuredContent") or result.get("content")
