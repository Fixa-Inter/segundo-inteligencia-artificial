import logging

from langchain.tools import ToolRuntime, tool

from app.schemas.UsuarioContexto import UsuarioContexto
from app.services.solicitacoes.buscarSolicitacao import (
    listar_minhas_solicitacoes as consultar_minhas_solicitacoes,
)

logger = logging.getLogger(__name__)


@tool
async def listar_minhas_solicitacoes(runtime: ToolRuntime) -> dict:
    """Lista solicitacoes do usuario autenticado.

Nao recebe filtros da IA. O SELECT usa o ID autenticado e restringe os
registros ao CNPJ do endereco do usuario."""
    try:
        contexto = runtime.context
        if not isinstance(contexto, dict) or not isinstance(contexto.get("usuario"), UsuarioContexto):
            raise ValueError("Forneça uma instância de UsuarioContexto em context['usuario'].")
        usuario = contexto["usuario"]
        if usuario.tipo_acesso.lower() not in ("tecnico", "solicitante"):
            return {
                "status": "ACESSO_NEGADO",
                "mensagem": "Somente técnicos e solicitantes podem realizar uma solicitação.",
            }

        return await consultar_minhas_solicitacoes(usuario)
    except Exception:
        logger.exception("Falha na tool listar_minhas_solicitacoes")
        raise
