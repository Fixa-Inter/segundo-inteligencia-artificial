from qdrant_client import models
from app.core.config import (
    QDRANT_CATEGORIA_COLLECTION,
    QDRANT_HISTORICO_COLLECTION,
    QDRANT_LOCAL_COLLECTION,
    QDRANT_TENANT_FIELD,
)
from app.core.clients.qdrant import abrir_cliente_qdrant


async def garantir_indice_historico() -> None:
    """Garante o indice de isolamento da memoria quando ela for utilizada."""
    async with abrir_cliente_qdrant() as cliente:
        if not QDRANT_HISTORICO_COLLECTION:
            print("Informações de conexão com o QDRANT ausentes!")
            return
        else:
            await cliente.create_payload_index(
                collection_name=QDRANT_HISTORICO_COLLECTION,
                field_name="user_id",
                field_schema=models.PayloadSchemaType.INTEGER,
                wait=True,
            )


async def garantir_indice_categoria_equipamento() -> None:
    """Garante o índice de isolamento por sede das categorias de equipamento."""
    async with abrir_cliente_qdrant() as cliente:
        if not QDRANT_CATEGORIA_COLLECTION:
                    print("Informações de conexão com o QDRANT ausentes!")
                    return
        await cliente.create_payload_index(
            collection_name=QDRANT_CATEGORIA_COLLECTION,
            field_name=QDRANT_TENANT_FIELD,
            field_schema=models.PayloadSchemaType.KEYWORD,
            wait=True,
        )


async def garantir_indice_local_endereco() -> None:
    """Garante o índice de isolamento por sede dos locais."""
    async with abrir_cliente_qdrant() as cliente:
        if not QDRANT_LOCAL_COLLECTION:
            print("Informações de conexão com o QDRANT ausentes!")
            return
        await cliente.create_payload_index(
            collection_name=QDRANT_LOCAL_COLLECTION,
            field_name=QDRANT_TENANT_FIELD,
            field_schema=models.PayloadSchemaType.KEYWORD,
            wait=True,
        )
