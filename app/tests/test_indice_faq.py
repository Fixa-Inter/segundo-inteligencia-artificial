"""O filtro do FAQ deve ter índice mesmo sem executar uma nova ingestão."""

import asyncio
from contextlib import asynccontextmanager
from importlib import import_module
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import FastAPI
from qdrant_client import models

from app.memory.vectorSearch import garantir_indice


@pytest.mark.parametrize("indices", [None, {}, {"perfil": object()}])
def test_garantir_indice_faq_cria_somente_se_ausente(monkeypatch, indices):
    cliente = SimpleNamespace(
        get_collection=AsyncMock(return_value=SimpleNamespace(payload_schema=indices)),
        create_payload_index=AsyncMock(),
    )

    @asynccontextmanager
    async def abrir_cliente():
        yield cliente

    monkeypatch.setattr(garantir_indice, "abrir_cliente_qdrant", abrir_cliente)

    asyncio.run(garantir_indice.garantir_indice_faq())

    cliente.get_collection.assert_awaited_once_with(
        collection_name=garantir_indice.configuracao.QDRANT_COLECAO_FAQ,
    )
    if indices and "perfil" in indices:
        cliente.create_payload_index.assert_not_awaited()
    else:
        cliente.create_payload_index.assert_awaited_once_with(
            collection_name=garantir_indice.configuracao.QDRANT_COLECAO_FAQ,
            field_name="perfil",
            field_schema=models.PayloadSchemaType.KEYWORD,
            wait=True,
        )


def test_lifespan_garante_indice_faq_antes_de_atender(monkeypatch):
    main = import_module("app.main")
    for nome in ("iniciar_cliente_mongo", "iniciar_cliente_qdrant"):
        monkeypatch.setattr(main, nome, Mock())
    for nome in (
        "fechar_conexoes_postgres", "fechar_cliente_databricks",
        "fechar_cliente_mongo", "fechar_cliente_qdrant",
        "garantir_indice_persistencia", "garantir_indice_historico",
        "garantir_indices_operacionais",
    ):
        monkeypatch.setattr(main, nome, AsyncMock())
    garantir_faq = AsyncMock()
    monkeypatch.setattr(main, "garantir_indice_faq", garantir_faq)

    async def verificar():
        async with main.lifespan(FastAPI()):
            garantir_faq.assert_awaited_once()

    asyncio.run(verificar())
