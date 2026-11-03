"""Contexto autenticado das ferramentas de cadastro; compartilhado entre domínios."""

from typing import Any

from langchain.tools import ToolRuntime
from app.schemas import UsuarioContexto
from app.core import MENSAGENS

def obter_contexto_cadastro(runtime: ToolRuntime) -> tuple[dict[str, Any], UsuarioContexto, str]:
    """Executa a etapa obter contexto cadastro no escopo de contexto. Usado pelo fluxo de tools."""
    contexto = runtime.context
    if not isinstance(contexto, dict) or not isinstance(contexto.get("usuario"), UsuarioContexto):
        raise ValueError(MENSAGENS['forneca_usuariocontexto_em_context_usuario_2'])

    sessao_id = contexto.get("session_id")
    if not isinstance(sessao_id, str) or not sessao_id.strip():
        raise ValueError(MENSAGENS['a_sessao_atual_nao_foi_informada_ao_agente'])
    if not isinstance(contexto.get("turno_id"), str) or not contexto["turno_id"].strip():
        raise ValueError(MENSAGENS['o_turno_atual_nao_foi_informado_ao_agente'])

    return contexto, contexto["usuario"], sessao_id
