from typing import Literal, cast

from langchain_core.messages import HumanMessage

from app.graph.context import GraphContext
from app.graph.state import GraphState
from app.graph.workflow import grafo
from app.schemas.UsuarioContexto import UsuarioContexto

from app.guardrails import anonimizar_entrada


Perfil = Literal[
    "solicitante",
    "tecnico",
    "gestor",
]

PERFIS_VALIDOS = {
    "solicitante",
    "tecnico",
    "gestor",
}


def criar_estado_inicial(
    mensagem: str,
    usuario: UsuarioContexto,
) -> GraphState:
    mensagem = mensagem.strip()

    if not mensagem:
        raise ValueError("A mensagem não pode estar vazia.")

    perfil_normalizado = usuario.tipo_acesso.strip().lower()

    if perfil_normalizado not in PERFIS_VALIDOS:
        raise ValueError("O perfil de usuário é inválido.")

    perfil = cast(Perfil, perfil_normalizado)

    return {
        "messages": [
            HumanMessage(content=mensagem),
        ],
        "user_id": str(usuario.usuario_id),
        "perfil": perfil,
        "tentativas": 0,
        "erro": None,
    }


async def executar_grafo(
    mensagem: str,
    usuario: UsuarioContexto,
    thread_id: str,
    imagens: list[str] | None = None,
) -> GraphState:
    thread_id = thread_id.strip()

    if not thread_id:
        raise ValueError("O thread_id não pode estar vazio.")

    estado_inicial = criar_estado_inicial(
        mensagem=mensagem,
        usuario=usuario,
    )

    contexto: GraphContext = {
        "usuario": usuario,
        "imagens": list(imagens or []),
    }

    thread_id_interno = (
        f"{usuario.usuario_id}:{thread_id}"
    )

    resultado = await grafo.ainvoke(
        estado_inicial,
        config={
            "configurable": {
                "thread_id": thread_id_interno,
            }
        },
        context=contexto,
    )

    return resultado