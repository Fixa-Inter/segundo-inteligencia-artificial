import asyncio
from langchain.tools import ToolRuntime, tool
from app.schemas import UsuarioContexto
from app.memory.vectorSearch.busca import buscar_local_endereco, buscar_categoria_equipamento
from app.core.clients.qdrant import abrir_cliente_qdrant
from app.services.gerais import obter_unidade_id


@tool
async def buscar_opcoes_ocorrencia(equipamento: str, local: str, runtime: ToolRuntime) -> dict:
    """Busca categoria do equipamento e local no Qdrant da sede autenticada.

    Informe descrições do relato. Não peça código ou ID de equipamento.
    Resolva candidatos ambíguos com o usuário antes de salvar a proposta.
    """
    contexto = runtime.context
    if not isinstance(contexto, dict) or not isinstance(contexto.get("usuario"), UsuarioContexto):
        raise ValueError("Forneça UsuarioContexto em context['usuario'].")
    usuario = contexto["usuario"]
    if usuario.tipo_acesso not in {"tecnico", "gestor", "administrador"}:
        return {"status": "ACESSO_NEGADO", "mensagem": "Somente técnicos e gestores podem preparar ocorrências."}
    unidade_id = await obter_unidade_id(usuario)
    async with abrir_cliente_qdrant() as cliente:
        categorias, locais = await asyncio.gather(
            buscar_categoria_equipamento(equipamento, unidade_id, cliente),
            buscar_local_endereco(local, unidade_id, cliente),
        )
    return {
        "status": "SUCESSO" if categorias and locais else "AGUARDANDO_INFORMACAO",
        "categoria_equipamento": {str(k): v for k, v in categorias.items()},
        "local_endereco": {str(k): v for k, v in locais.items()},
        "mensagem": "Confirme os candidatos; peça detalhes se faltar categoria ou local.",
    }
