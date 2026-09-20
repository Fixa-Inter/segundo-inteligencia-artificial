from langchain_core.messages import HumanMessage

from app.graph.workflow import grafo
from app.schemas.UsuarioContexto import UsuarioContexto
from app.schemas.chat import ChatRequest, ChatResponse


async def processar_chat(
    dados: ChatRequest,
    usuario: UsuarioContexto,
) -> ChatResponse:
    thread_id_interno = (
        f"{usuario.usuario_id}:{dados.thread_id}"
    )

    resultado = await grafo.ainvoke(
        {
            "messages": [
                HumanMessage(content=dados.mensagem),
            ],
            "user_id": str(usuario.usuario_id),
            "perfil": usuario.tipo_acesso.lower(),
            "tentativas": 0,
        },
        config={
            "configurable": {
                "thread_id": thread_id_interno,
            }
        },
        context={
            "usuario": usuario,
            "imagens": dados.imagens,
        },
    )

    return ChatResponse(
        thread_id=dados.thread_id,
        intencao=resultado.get("intencao"),
        resposta=resultado.get(
            "resposta_final",
            "Não foi possível produzir uma resposta.",
        ),
    )