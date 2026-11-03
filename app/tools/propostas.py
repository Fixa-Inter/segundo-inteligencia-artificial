"""Descrição verificável dos campos relacionais apresentados ao usuário."""

from app.core.clients import abrir_cliente_qdrant
from app.core import QDRANT_COLECAO_CATEGORIA, QDRANT_COLECAO_LOCAL
from app.memory.vectorSearch import validar_selecao
from app.services.gerais import obter_unidade_id

async def resolver_rotulos(dados: dict, usuario) -> dict[str, str]:
    """Confere IDs Qdrant e resolve rótulos de categoria/local da unidade. Usado pelo fluxo de tools."""
    unidade_id = await obter_unidade_id(usuario)
    async with abrir_cliente_qdrant() as cliente:
        categoria = await validar_selecao(QDRANT_COLECAO_CATEGORIA, dados["categoria_equipamento_id"], unidade_id, cliente)
        local = await validar_selecao(QDRANT_COLECAO_LOCAL, dados["local_endereco_id"], unidade_id, cliente)
    return {"categoria_equipamento_id": categoria, "local_endereco_id": local}
