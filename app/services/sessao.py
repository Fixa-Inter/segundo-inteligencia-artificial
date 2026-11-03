from fastapi import HTTPException, status
from app.graph import grafo
from app.memory.persistencia.sessoes import encerrar_sessao
from app.schemas import UsuarioContexto, EncerrarSessaoSaida
from app.core import MENSAGENS

async def finalizar_sessao_chat(
    thread_id: str,
    usuario: UsuarioContexto,
) -> EncerrarSessaoSaida:
    """Encerra persistência da sessão própria e remove seu checkpoint quando disponível. Usado pelo fluxo de services."""
    thread_id = thread_id.strip()

    # Validação: rejeita entrada/contexto incompatível antes de prosseguir.
    if not thread_id:
        raise ValueError(
            MENSAGENS['o_thread_id_nao_pode_estar_vazio']
        )

    resultado = await encerrar_sessao(
        sessao_id=thread_id,
        usuario_id=usuario.usuario_id,
    )

    if resultado is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=MENSAGENS['conversa_nao_encontrada'],
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
        mensagem=MENSAGENS['sessao_encerrada_com_sucesso'],
        titulo=resultado["titulo"] or None,
        resumo=resultado["resumo"] or None,
    )
