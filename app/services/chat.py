import uuid
import time
from fastapi import HTTPException, status
from app.graph.runner import PERFIS_VALIDOS, executar_grafo
from app.schemas.UsuarioContexto import UsuarioContexto
from app.schemas.chat import ChatRequest, ChatResponse
from app.memory.persistencia.sessoes.iniciar_sessao import iniciar_sessao
from app.memory.persistencia.utilitarios import documento_id_da_sessao
from app.observability.metrics import (
    CHAT_RESPONSE_SECONDS,
    CHAT_REQUESTS,
    reset_request_cost,
    restore_request_cost,
    reset_request_outcome,
    restore_request_outcome,
    mark_request_failed,
    request_failed,
    reset_pending_resolutions,
    restore_pending_resolutions,
)


async def _processar_chat(
    dados: ChatRequest,
    usuario: UsuarioContexto,
) -> ChatResponse:
    if usuario.tipo_acesso.strip().lower() not in PERFIS_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Perfil sem permissão de acesso ao chat.",
        )

    if dados.thread_id is None:
        session_id = str(uuid.uuid4())
        dados.thread_id = session_id
        await iniciar_sessao(session_id=session_id,user_id=usuario.usuario_id)
    else:
        doc_id = await documento_id_da_sessao(
            session_id=dados.thread_id,
            user_id=usuario.usuario_id,
        )

        if doc_id is None:
            raise HTTPException(
                status_code=404,
                detail="Conversa não encontrada.",
            )
    
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


async def processar_chat(
    dados: ChatRequest,
    usuario: UsuarioContexto,
) -> ChatResponse:
    inicio = time.perf_counter()
    token_custo = reset_request_cost()
    token_resultado = reset_request_outcome()
    token_resolucoes = reset_pending_resolutions()
    try:
        return await _processar_chat(dados, usuario)
    except Exception:
        # Falhas antes de o grafo iniciar também entram no denominador.
        mark_request_failed()
        raise
    finally:
        CHAT_REQUESTS.labels("error" if request_failed() else "success").inc()
        CHAT_RESPONSE_SECONDS.observe(time.perf_counter() - inicio)
        restore_request_cost(token_custo)
        restore_request_outcome(token_resultado)
        restore_pending_resolutions(token_resolucoes)
