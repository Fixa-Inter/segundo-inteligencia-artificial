"""Testes do pool HTTP compartilhado para Databricks."""

import asyncio

from app.core.clients import databricks


def test_cliente_http_reutiliza_o_pool(monkeypatch):
    monkeypatch.setattr(databricks, "_CLIENTE_HTTP", None)

    primeiro = databricks.obter_cliente_databricks()
    segundo = databricks.obter_cliente_databricks()
    asyncio.run(databricks.fechar_cliente_databricks())

    assert primeiro is segundo
    assert primeiro.is_closed
    assert databricks._CLIENTE_HTTP is None
