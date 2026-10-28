from fastapi import HTTPException, status

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

    resultado = await encerrar_sessao(
        sessao_id=thread_id,
        usuario_id=usuario.usuario_id,
    )

    if resultado is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversa não encontrada.",
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
        titulo=resultado["titulo"] or None,
        resumo=resultado["resumo"] or None,
    )
