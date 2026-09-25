from app.graph.workflow import grafo
from app.memory.persistencia.sessoes.encerrar_sessao import (
    encerrar_sessao,
)
from app.schemas.UsuarioContexto import UsuarioContexto
from app.schemas.sessao import EncerrarSessaoResponse


async def finalizar_sessao_chat(
    thread_id: str,
    usuario: UsuarioContexto,
) -> EncerrarSessaoResponse:
    thread_id = thread_id.strip()

    if not thread_id:
        raise ValueError(
            "O thread_id não pode estar vazio."
        )

    resumo = await encerrar_sessao(
        session_id=thread_id,
        user_id=usuario.usuario_id,
    )

    thread_id_interno = (
        f"{usuario.usuario_id}:{thread_id}"
    )

    checkpointer = grafo.checkpointer

    if checkpointer is not None:
        await checkpointer.adelete_thread(
            thread_id_interno
        )

    return EncerrarSessaoResponse(
        thread_id=thread_id,
        status="ENCERRADA",
        mensagem="Sessão encerrada com sucesso.",
        resumo=resumo or None,
    )