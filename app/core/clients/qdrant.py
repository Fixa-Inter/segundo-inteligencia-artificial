from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from qdrant_client import AsyncQdrantClient

from app.core import configuracao


@asynccontextmanager
async def abrir_cliente_qdrant() -> AsyncIterator[AsyncQdrantClient]:
    """Disponibiliza um cliente sob demanda e o fecha mesmo em caso de erro."""
    if not configuracao.QDRANT_URL:
        raise ValueError("Configure QDRANT_URL.")
    cliente = AsyncQdrantClient(
        url=configuracao.QDRANT_URL, api_key=configuracao.QDRANT_CHAVE_API,
        timeout=configuracao.QDRANT_TIMEOUT_SECONDS,
    )
    try:
        yield cliente
    finally:
        await cliente.close()
