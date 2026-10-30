"""Autorização interna das tools de indicadores, sem argumentos do modelo."""

import logging

from langchain.tools import ToolRuntime

from app.schemas import UsuarioContexto
from app.services.gerais.unidade import obter_unidade_id
from app.services.indicadores.gerais.unidade import validar_unidade_id


registrador = logging.getLogger(__name__)


def validar_gestor(runtime: ToolRuntime) -> dict | None:
    contexto = getattr(runtime, "context", None)
    if not isinstance(contexto, dict) or not isinstance(
        contexto.get("usuario"), UsuarioContexto,
    ):
        return {
            "status": "ACESSO_NEGADO",
            "mensagem": "Contexto autenticado indisponível para consultar indicadores.",
        }
    usuario = contexto["usuario"]
    if usuario.tipo_acesso != "gestor":
        return {
            "status": "ACESSO_NEGADO",
            "mensagem": "Somente gestores podem consultar indicadores.",
        }
    if usuario.usuario_id <= 0:
        return {
            "status": "ACESSO_NEGADO",
            "mensagem": "Usuário autenticado inválido para consultar indicadores.",
        }
    return None


async def resolver_unidade_indicadores(runtime: ToolRuntime) -> int | dict:
    """Resolve a unidade atual no servidor; nunca aceita IDs da conversa."""
    negado = validar_gestor(runtime)
    if negado:
        return negado

    try:
        unidade_id = await obter_unidade_id(runtime.context["usuario"])
    except (PermissionError, ValueError):
        return {
            "status": "ACESSO_NEGADO",
            "mensagem": "Não foi possível validar sua unidade para consultar indicadores.",
        }
    except Exception:
        # Não registra a exceção: mensagens de drivers podem conter credenciais.
        registrador.error("Falha ao resolver a unidade autenticada dos indicadores.")
        return {
            "status": "ERRO_FERRAMENTA",
            "mensagem": "Não foi possível consultar os indicadores agora.",
        }

    if validar_unidade_id(unidade_id):
        return {
            "status": "ACESSO_NEGADO",
            "mensagem": "Unidade autenticada inválida para consultar indicadores.",
        }
    return unidade_id
