from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from app.core.config import MONGODB_URI, MONGO_BANCO_DADOS, MONGO_COLLECTION_SESSOES
from pymongo import AsyncMongoClient


def validar_config_mongo() -> None:
    """Interrompe a operação quando faltar configuração da persistência."""
    configuracoes = {
        "MONGO_URI": MONGODB_URI,
        "MONGO_BANCO_DADOS": MONGO_BANCO_DADOS,
        "MONGO_COLLECTION_SESSOES": MONGO_COLLECTION_SESSOES,
    }
    ausentes = [
        nome for nome, valor in configuracoes.items()
        if not isinstance(valor, str) or not valor.strip()
    ]
    if ausentes:
        raise RuntimeError(
            "Configuração do MongoDB ausente: " + ", ".join(ausentes)
        )


@asynccontextmanager
async def abrir_cliente_mongo() -> AsyncIterator[AsyncMongoClient]:
    """Disponibiliza um cliente sob demanda e o fecha mesmo em caso de erro."""
    validar_config_mongo()
    cliente = AsyncMongoClient(MONGODB_URI)
    try:
        yield cliente
    finally:
        await cliente.close()


