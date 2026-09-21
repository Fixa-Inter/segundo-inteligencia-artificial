from app.graph.runner import executar_grafo
from app.schemas.UsuarioContexto import UsuarioContexto
from app.schemas.chat import ChatRequest, ChatResponse


async def processar_chat(
    dados: ChatRequest,
    usuario: UsuarioContexto,
) -> ChatResponse:
    resultado = await executar_grafo(
        mensagem=dados.mensagem,
        usuario=usuario,
        thread_id=dados.thread_id,
        imagens=dados.imagens,
    )

    return ChatResponse(
        thread_id=dados.thread_id,
        intencao=resultado.get("intencao"),
        resposta=resultado.get(
            "resposta_final",
            "Não foi possível produzir uma resposta.",
        ),
    )