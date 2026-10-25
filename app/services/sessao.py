from app.services.disponibilidade import validar_chaves_ia
from app.services.historico_web import obter_conversa_web, atualizar_estado_conversa
from app.memory.persistencia.utilitarios import agora
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

    historico = await obter_conversa_web(thread_id, usuario.usuario_id)
    if historico.closed:
        return EncerrarSessaoSaida(thread_id=thread_id, status="ENCERRADA", mensagem="Sessão já encerrada.", resumo=None)
    validar_chaves_ia()
    from app.graph.fluxo import grafo

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

    await atualizar_estado_conversa(thread_id, usuario.usuario_id, encerrada_em=agora(), confirmacao="nao")

    return EncerrarSessaoSaida(
        thread_id=thread_id,
        status="ENCERRADA",
        mensagem="Sessão encerrada com sucesso.",
        resumo=resumo or None,
    )