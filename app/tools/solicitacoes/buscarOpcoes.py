import asyncio

from langchain.tools import ToolRuntime, tool
from app.memory.vectorSearch import buscar_categoria_equipamento, buscar_local_endereco
from app.memory.vectorSearch.cliente import abrir_cliente_qdrant
from app.schemas.UsuarioContexto import UsuarioContexto


@tool
async def buscar_opcoes_solicitacao(
    equipamento: str, local: str, runtime: ToolRuntime
) -> dict:
    """Busca categorias do equipamento e locais da sede autenticada.

    Forneça descrições extraídas da conversa. Resultados são candidatos, não
    uma decisão automática: esclareça ambiguidades antes de preparar a criação.
    """
    contexto = runtime.context
    if not isinstance(contexto, dict) or not isinstance(contexto.get("usuario"), UsuarioContexto):
        raise ValueError("Forneça uma instância de UsuarioContexto em context['usuario'].")
    usuario = contexto["usuario"]
    async with abrir_cliente_qdrant() as cliente:
        async with asyncio.TaskGroup() as tarefas:
            categorias = tarefas.create_task(
                buscar_categoria_equipamento(equipamento, usuario.endereco_id, cliente)
            )
            locais = tarefas.create_task(
                buscar_local_endereco(local, usuario.endereco_id, cliente)
            )
    return {
        "categoria_equipamento": {str(k): v for k, v in categorias.result().items()},
        "local_endereco": {str(k): v for k, v in locais.result().items()},
    }
