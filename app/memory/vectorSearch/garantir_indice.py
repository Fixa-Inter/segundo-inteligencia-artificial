from qdrant_client import models
from app.core.config import QDRANT_HISTORICO_COLLECTION
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
