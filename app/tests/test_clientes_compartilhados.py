"""Ciclo de vida dos clientes compartilhados de MongoDB e Qdrant."""

import asyncio
from importlib import import_module
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import FastAPI

from app.core.clients import mongo, qdrant


def test_mongo_reutiliza_cliente_e_fecha_no_encerramento(monkeypatch):
    clientes = []

    def criar_cliente(uri):
        cliente = Mock()
        cliente.close = AsyncMock()
        clientes.append(cliente)
        return cliente

    monkeypatch.setattr(mongo, "MONGODB_URI", "mongodb://localhost:27017")
    monkeypatch.setattr(mongo, "_CLIENTE_MONGO", None)
    monkeypatch.setattr(mongo, "AsyncMongoClient", criar_cliente)

    async def verificar():
        mongo.iniciar_cliente_mongo()
        async with mongo.abrir_cliente_mongo() as primeiro:
            async with mongo.abrir_cliente_mongo() as segundo:
                assert primeiro is segundo
        primeiro.close.assert_not_awaited()
        await mongo.fechar_cliente_mongo()
        primeiro.close.assert_awaited_once()
        await mongo.fechar_cliente_mongo()
        assert len(clientes) == 1

        async with mongo.abrir_cliente_mongo() as novo:
            assert novo is not primeiro
        novo.close.assert_awaited_once()

    asyncio.run(verificar())
    assert len(clientes) == 2


def test_lifespan_fecha_clientes_se_indice_falhar(monkeypatch):
    main = import_module("app.main")
    fechar_mongo = AsyncMock()
    fechar_qdrant = AsyncMock()
    fechar_databricks = AsyncMock()
    fechar_postgres = AsyncMock()

    monkeypatch.setattr(main, "iniciar_cliente_mongo", Mock())
    monkeypatch.setattr(main, "iniciar_cliente_qdrant", Mock())
    monkeypatch.setattr(
        main, "garantir_indice_persistencia", AsyncMock(side_effect=RuntimeError("indice")),
    )
    monkeypatch.setattr(main, "fechar_cliente_mongo", fechar_mongo)
    monkeypatch.setattr(main, "fechar_cliente_qdrant", fechar_qdrant)
    monkeypatch.setattr(main, "fechar_cliente_databricks", fechar_databricks)
    monkeypatch.setattr(main, "fechar_conexoes_postgres", fechar_postgres)

    async def verificar():
        with pytest.raises(RuntimeError, match="indice"):
            async with main.lifespan(FastAPI()):
                pass

    asyncio.run(verificar())
    fechar_mongo.assert_awaited_once()
    fechar_qdrant.assert_awaited_once()
    fechar_databricks.assert_awaited_once()
    fechar_postgres.assert_awaited_once()


def test_qdrant_reutiliza_cliente_e_fecha_no_encerramento(monkeypatch):
    clientes = []

    def criar_cliente(**kwargs):
        cliente = Mock()
        cliente.close = AsyncMock()
        clientes.append(cliente)
        return cliente

    monkeypatch.setattr(qdrant.configuracao, "QDRANT_URL", "http://localhost:6333")
    monkeypatch.setattr(qdrant, "_CLIENTE_QDRANT", None)
    monkeypatch.setattr(qdrant, "AsyncQdrantClient", criar_cliente)

    async def verificar():
        qdrant.iniciar_cliente_qdrant()
        async with qdrant.abrir_cliente_qdrant() as primeiro:
            async with qdrant.abrir_cliente_qdrant() as segundo:
                assert primeiro is segundo
        primeiro.close.assert_not_awaited()
        await qdrant.fechar_cliente_qdrant()
        primeiro.close.assert_awaited_once()
        await qdrant.fechar_cliente_qdrant()
        assert len(clientes) == 1

        async with qdrant.abrir_cliente_qdrant() as novo:
            assert novo is not primeiro
        novo.close.assert_awaited_once()

    asyncio.run(verificar())
    assert len(clientes) == 2
