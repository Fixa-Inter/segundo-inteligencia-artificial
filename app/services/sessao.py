from app.graph.fluxo import grafo
from app.memory.persistencia.sessoes import (
    encerrar_sessao,
)
from app.schemas import UsuarioContexto
from app.schemas import EncerrarSessaoSaida


async def finalizar_sessao_chat(
    thread_id: str,
    usuario: UsuarioContexto,
) -> EncerrarSessaoSaida:
    thread_id = thread_id.strip()

    if not thread_id:
        raise ValueError(
            "O thread_id não pode estar vazio."
        )

    resumo = await encerrar_sessao(
        sessao_id=thread_id,
        usuario_id=usuario.usuario_id,
    )

    sessao_id_interno = (
        f"{usuario.usuario_id}:{thread_id}"
    )

    checkpointer = grafo.checkpointer

    if checkpointer is not None:
        await checkpointer.adelete_thread(
            sessao_id_interno
        )

    return EncerrarSessaoSaida(
        thread_id=thread_id,
        status="ENCERRADA",
        mensagem="Sessão encerrada com sucesso.",
        resumo=resumo or None,
    )