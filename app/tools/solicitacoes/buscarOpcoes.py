import asyncio

from langchain.tools import ToolRuntime, tool
from app.memory.vectorSearch import buscar_categoria_equipamento, buscar_local_endereco


@tool
async def buscar_opcoes_solicitacao(
    equipamento: str, local: str, runtime: ToolRuntime
) -> dict:
    """Busca categorias do equipamento e locais da sede autenticada.

    Forneça descrições extraídas da conversa. Resultados são candidatos, não
    uma decisão automática: esclareça ambiguidades antes de preparar a criação.
    """
    contexto = runtime.context
    if not isinstance(contexto, dict):
        raise ValueError("Forneça endereco_id e qdrant no contexto da aplicação.")
    categorias, locais = await asyncio.gather(
        buscar_categoria_equipamento(equipamento, contexto["endereco_id"], contexto["qdrant"]),
        buscar_local_endereco(local, contexto["endereco_id"], contexto["qdrant"]),
    )
    return {
        "categoria_equipamento": {str(k): v for k, v in categorias.items()},
        "local_endereco": {str(k): v for k, v in locais.items()},
    }
