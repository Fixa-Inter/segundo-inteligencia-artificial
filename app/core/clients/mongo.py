from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from app.core.config import MONGODB_URI
from pymongo import AsyncMongoClient


@asynccontextmanager
async def abrir_cliente_mongo() -> AsyncIterator[AsyncMongoClient]:
    """Disponibiliza um cliente sob demanda e o fecha mesmo em caso de erro."""
    if not MONGODB_URI:
        raise ValueError("Configure MONGO_URI.")
    cliente = AsyncMongoClient(MONGODB_URI)
    try:
        yield cliente
    finally:
        await cliente.close()


