from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from qdrant_client import AsyncQdrantClient

from app.core import config


@asynccontextmanager
async def abrir_cliente_qdrant() -> AsyncIterator[AsyncQdrantClient]:
    """Disponibiliza um cliente sob demanda e o fecha mesmo em caso de erro."""
    if not config.QDRANT_URL:
        raise ValueError("Configure QDRANT_URL.")
    cliente = AsyncQdrantClient(
        url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY,
    )
    try:
        yield cliente
    finally:
        await cliente.close()
