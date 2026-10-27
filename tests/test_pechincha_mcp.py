import asyncio

import httpx
import pytest

from app.mcp.pechincha import ferramentas, transporte
from app.mcp.pechincha.modelos import BuscaOfertas, normalizar_ofertas


def test_mcp_session_and_structured_search(monkeypatch):
    chamadas = []

    async def fake_post(cliente, corpo, headers):
        chamadas.append((corpo, dict(headers)))
        if corpo["method"] == "initialize":
            return httpx.Response(200, headers={"Mcp-Session-Id": "s1"}, json={"jsonrpc": "2.0", "id": 1,
                "result": {"protocolVersion": transporte.VERSAO_PROTOCOLO, "capabilities": {}}})
        if corpo["method"] == "notifications/initialized":
            return httpx.Response(202)
        return httpx.Response(200, json={"jsonrpc": "2.0", "id": 2, "result": {
            "structuredContent": {"deals": [{"title": "Furadeira 220 V", "store": "Amazon",
                "price": 199.9, "url": "https://pechincha.ai/p/abc/furadeira"}],
                "total": 1, "page": 1, "pages": 1}}})

    monkeypatch.setattr(transporte, "_post", fake_post)
    resultado = asyncio.run(ferramentas.buscar_ofertas(BuscaOfertas(query="furadeira", max_price=200)))
    assert [corpo["method"] for corpo, _ in chamadas] == [
        "initialize", "notifications/initialized", "tools/call"]
    assert chamadas[-1][1]["Mcp-Session-Id"] == "s1"
    assert chamadas[-1][0]["params"] == {"name": "search_deals", "arguments": {
        "query": "furadeira", "max_price": 200.0, "page": 1}}
    assert resultado["ofertas"][0]["store_name"] == "Amazon"
    assert resultado["ofertas"][0]["url"].startswith("https://pechincha.ai/p/")


def test_sse_and_tool_error_are_handled(monkeypatch):
    async def fake_post(cliente, corpo, headers):
        if corpo["method"] == "initialize":
            return httpx.Response(200, json={"jsonrpc": "2.0", "id": 1,
                "result": {"protocolVersion": transporte.VERSAO_PROTOCOLO}})
        if corpo["method"] == "notifications/initialized":
            return httpx.Response(202)
        return httpx.Response(200, headers={"Content-Type": "text/event-stream"},
            text='event: message\ndata: {"jsonrpc":"2.0","id":2,"result":{"isError":true,"content":[{"type":"text","text":"Filtro inválido"}]}}\n\n')

    monkeypatch.setattr(transporte, "_post", fake_post)
    with pytest.raises(transporte.ErroPechincha) as erro:
        asyncio.run(ferramentas.listar_categorias())
    assert erro.value.codigo == "ferramenta"


def test_empty_deals_are_success_but_bad_shape_is_error():
    assert normalizar_ofertas({"deals": [], "total": 0})["ofertas"] == []
    with pytest.raises(transporte.ErroPechincha):
        normalizar_ofertas({"products": []})


def test_only_query_is_required_and_price_range_must_be_valid():
    assert BuscaOfertas(query="broca").model_dump(exclude_none=True) == {"query": "broca", "page": 1}
    with pytest.raises(ValueError):
        BuscaOfertas(query=" ")
    with pytest.raises(ValueError):
        BuscaOfertas(query="broca", min_price=200, max_price=100)
