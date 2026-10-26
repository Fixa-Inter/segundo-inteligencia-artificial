from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from qdrant_client import AsyncQdrantClient

from app.core import configuracao


_CLIENTE_QDRANT: AsyncQdrantClient | None = None


def iniciar_cliente_qdrant() -> None:
    """Cria o cliente compartilhado para o lifespan da aplicacao."""
    global _CLIENTE_QDRANT
    if _CLIENTE_QDRANT is None:
        if not configuracao.QDRANT_URL:
            raise ValueError("Configure QDRANT_URL.")
        _CLIENTE_QDRANT = AsyncQdrantClient(
            url=configuracao.QDRANT_URL, api_key=configuracao.QDRANT_CHAVE_API,
        )


@asynccontextmanager
async def abrir_cliente_qdrant() -> AsyncIterator[AsyncQdrantClient]:
    """Reutiliza o cliente no lifespan; fora dele, fecha ao sair."""
    if _CLIENTE_QDRANT is not None:
        yield _CLIENTE_QDRANT
    else:
        if not configuracao.QDRANT_URL:
            raise ValueError("Configure QDRANT_URL.")
        cliente = AsyncQdrantClient(
            url=configuracao.QDRANT_URL, api_key=configuracao.QDRANT_CHAVE_API,
        )
        try:
            yield cliente
        finally:
            await cliente.close()


async def fechar_cliente_qdrant() -> None:
    """Fecha as conexoes do cliente no encerramento da aplicacao."""
    global _CLIENTE_QDRANT
    if _CLIENTE_QDRANT is not None:
        cliente = _CLIENTE_QDRANT
        _CLIENTE_QDRANT = None
        await cliente.close()
