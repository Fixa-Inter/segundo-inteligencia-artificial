"""Autorização interna das tools de indicadores, sem argumentos do modelo."""


import logging

from langchain.tools import ToolRuntime

from app.schemas import UsuarioContexto
from app.services.gerais.unidade import obter_unidade_id
from app.services.indicadores.gerais.unidade import validar_unidade_id

from app.core.respostas import MENSAGENS


registrador = logging.getLogger(__name__)


def validar_gestor(runtime: ToolRuntime, *, perfis_permitidos=frozenset({"gestor", "administrador"})) -> dict | None:
    contexto = getattr(runtime, "context", None)
    if not isinstance(contexto, dict) or not isinstance(
        contexto.get("usuario"), UsuarioContexto,
    ):
        return {
            "status": "ACESSO_NEGADO",
            "mensagem": MENSAGENS['contexto_autenticado_indisponivel_para_consultar_indicadores'],
        }
    usuario = contexto["usuario"]
    if usuario.tipo_acesso not in perfis_permitidos:
        return {
            "status": "ACESSO_NEGADO",
            "mensagem": MENSAGENS['somente_gestores_e_administradores_podem_consultar_indicadores'],
        }
    if usuario.usuario_id <= 0:
        return {
            "status": "ACESSO_NEGADO",
            "mensagem": MENSAGENS['usuario_autenticado_invalido_para_consultar_indicadores'],
        }
    return None


async def resolver_unidade_indicadores(runtime: ToolRuntime, *, perfis_permitidos=frozenset({"gestor", "administrador"})) -> int | dict:
    """Resolve a unidade atual no servidor; nunca aceita IDs da conversa."""
    negado = validar_gestor(runtime, perfis_permitidos=perfis_permitidos)
    if negado:
        return negado

    try:
        unidade_id = await obter_unidade_id(runtime.context["usuario"])
    except (PermissionError, ValueError):
        return {
            "status": "ACESSO_NEGADO",
            "mensagem": MENSAGENS['nao_foi_possivel_validar_sua_unidade_para_consultar_indicadores'],
        }
    except Exception:
        # Não registra a exceção: mensagens de drivers podem conter credenciais.
        registrador.error("Falha ao resolver a unidade autenticada dos indicadores.")
        return {
            "status": "ERRO_FERRAMENTA",
            "mensagem": MENSAGENS['nao_foi_possivel_consultar_os_indicadores_agora'],
        }

    if validar_unidade_id(unidade_id):
        return {
            "status": "ACESSO_NEGADO",
            "mensagem": MENSAGENS['unidade_autenticada_invalida_para_consultar_indicadores'],
        }
    return unidade_id
