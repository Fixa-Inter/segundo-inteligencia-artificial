"""Prepara collections vazias para a primeira execução local."""

from qdrant_client import models
from app.core import configuracao
from app.core.clients.qdrant import abrir_cliente_qdrant


async def garantir_collections() -> None:
    colecoes = set(configuracao.QDRANT_COLECOES_OPERACIONAIS) | {
        configuracao.QDRANT_COLECAO_HISTORICO,
        configuracao.QDRANT_COLECAO_FAQ,
        configuracao.QDRANT_COLECAO_CATEGORIA,
    }
    async with abrir_cliente_qdrant() as cliente:
        for colecao in sorted(colecoes):
            if not await cliente.collection_exists(colecao):
                try:
                    await cliente.create_collection(
                        collection_name=colecao,
                        vectors_config=models.VectorParams(
                            size=configuracao.DIMENSOES_VETORIZACAO_OPERACIONAL,
                            distance=models.Distance.COSINE,
                        ),
                    )
                except Exception:
                    # Outra réplica pode ter criado a collection neste intervalo.
                    if not await cliente.collection_exists(colecao):
                        raise
