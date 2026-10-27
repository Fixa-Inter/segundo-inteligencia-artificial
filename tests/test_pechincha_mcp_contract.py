"""Contrato ao vivo: execute com RUN_PECHINCHA_LIVE_TESTS=1."""

import asyncio
import os

import pytest

from app.mcp.pechincha import buscar_ofertas, listar_categorias, listar_lojas
from app.mcp.pechincha.modelos import BuscaOfertas


pytestmark = pytest.mark.skipif(os.getenv("RUN_PECHINCHA_LIVE_TESTS") != "1",
                                reason="Consulta o serviço público; execute explicitamente.")


def test_public_tools_contract():
    lojas = asyncio.run(listar_lojas("amazon"))
    assert any(loja.get("slug") == "amazon" for loja in lojas)
    categorias = asyncio.run(listar_categorias())
    assert categorias and all(categoria.get("slug") for categoria in categorias)
    resultado = asyncio.run(buscar_ofertas(BuscaOfertas(query="ar condicionado")))
    assert isinstance(resultado["ofertas"], list)
    assert isinstance(resultado["total"], int)
    for oferta in resultado["ofertas"]:
        assert oferta["title"]
        assert oferta["url"] and oferta["url"].startswith("https://")
