from langchain.tools import ToolRuntime, tool

from app.core.clients.qdrant import abrir_cliente_qdrant
from app.memory.vectorSearch import buscar_local_endereco
from app.services.gerais import obter_unidade_id
from app.tools.solicitacoes.criarSolicitacao import _contexto

from app.core.respostas import MENSAGENS


@tool
async def buscar_opcoes_evento(local: str, runtime: ToolRuntime) -> dict:
    """Busca locais ativos da unidade autenticada para um evento.

    Use somente IDs retornados; esclareça candidatos ausentes ou ambíguos.
    Disponível para gestores e administradores na web e no mobile.
    """
    _, usuario, _ = _contexto(runtime)
    if usuario.tipo_acesso not in {"gestor", "administrador"}:
        return {"status": "ACESSO_NEGADO", "mensagem": MENSAGENS['somente_gestores_e_administradores_podem_criar_eventos']}
    unidade_id = await obter_unidade_id(usuario)
    async with abrir_cliente_qdrant() as cliente:
        locais = await buscar_local_endereco(local, unidade_id, cliente)
    return {"local_unidade": {str(k): v for k, v in locais.items()}}
