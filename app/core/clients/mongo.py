from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from app.core.configuracao import MONGODB_URI, MONGO_BANCO_DADOS, MONGO_COLECAO_SESSOES
from pymongo import AsyncMongoClient


_CLIENTE_MONGO: AsyncMongoClient | None = None


def validar_config_mongo() -> None:
    """Interrompe a operação quando faltar configuração da persistência."""
    configuracoes = {
        "MONGO_URI": MONGODB_URI,
        "MONGO_BANCO_DADOS": MONGO_BANCO_DADOS,
        "MONGO_COLECAO_SESSOES": MONGO_COLECAO_SESSOES,
    }
    ausentes = [
        nome for nome, valor in configuracoes.items()
        if not isinstance(valor, str) or not valor.strip()
    ]
    if ausentes:
        raise RuntimeError(
            "Configuração do MongoDB ausente: " + ", ".join(ausentes)
        )


def iniciar_cliente_mongo() -> None:
    """Cria o pool compartilhado para o lifespan da aplicacao."""
    global _CLIENTE_MONGO
    if _CLIENTE_MONGO is None:
        validar_config_mongo()
        _CLIENTE_MONGO = AsyncMongoClient(MONGODB_URI)


@asynccontextmanager
async def abrir_cliente_mongo() -> AsyncIterator[AsyncMongoClient]:
    """Reutiliza o pool no lifespan; fora dele, fecha o cliente ao sair."""
    if _CLIENTE_MONGO is not None:
        yield _CLIENTE_MONGO
    else:
        validar_config_mongo()
        cliente = AsyncMongoClient(MONGODB_URI)
        try:
            yield cliente
        finally:
            await cliente.close()


async def fechar_cliente_mongo() -> None:
    """Fecha o cliente e seu pool no encerramento da aplicacao."""
    global _CLIENTE_MONGO
    if _CLIENTE_MONGO is not None:
        cliente = _CLIENTE_MONGO
        _CLIENTE_MONGO = None
        await cliente.close()


