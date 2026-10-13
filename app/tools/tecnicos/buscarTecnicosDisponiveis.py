from langchain.tools import ToolRuntime, tool

from app.schemas.UsuarioContexto import UsuarioContexto
from app.services.tecnicos.buscarTecnicosDisponiveis import (
    buscar_tecnicos_disponiveis as consultar_tecnicos_disponiveis,
)


@tool
async def buscar_tecnicos_disponiveis(runtime: ToolRuntime) -> dict:
    """Busca técnicos do endereço do gestor com menor carga de OS fora de Finalizadas (ID 4)."""
    contexto = runtime.context
    if not isinstance(contexto, dict) or not isinstance(
        contexto.get("usuario"), UsuarioContexto
    ):
        raise ValueError("Forneca UsuarioContexto em context['usuario'].")

    return await consultar_tecnicos_disponiveis(contexto["usuario"])
