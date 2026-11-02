"""Ferramenta de leitura sem argumentos de identidade fornecidos pelo modelo."""

import logging

from langchain.tools import ToolRuntime, tool
from app.schemas import UsuarioContexto
from app.core.respostas import MENSAGENS
from app.services.feedback.listarFeedbacks import listar_feedbacks


@tool
async def listar_meus_feedbacks(runtime: ToolRuntime) -> dict:
    """Lista os feedbacks do usuário autenticado, do mais recente ao mais antigo."""
    usuario = runtime.context.get("usuario") if isinstance(runtime.context, dict) else None
    if not isinstance(usuario, UsuarioContexto):
        return {"status": "ACESSO_NEGADO", "mensagem": MENSAGENS["contexto_de_autenticacao_invalido"]}
    try:
        return await listar_feedbacks(usuario)
    except PermissionError as erro:
        return {"status": "ACESSO_NEGADO", "mensagem": str(erro)}
    except Exception:
        logging.getLogger(__name__).exception("Falha ao consultar feedbacks")
        return {"status": "ERRO_FERRAMENTA", "mensagem": MENSAGENS["feedbacks_erro_consulta"]}
