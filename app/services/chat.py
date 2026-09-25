import uuid
from fastapi import HTTPException, status
from app.graph.runner import PERFIS_VALIDOS, executar_grafo
from app.schemas.UsuarioContexto import UsuarioContexto
from app.schemas.chat import ChatRequest, ChatResponse
from app.memory.persistencia.sessoes.iniciar_sessao import iniciar_sessao
from app.memory.persistencia.utilitarios import documento_id_da_sessao


async def processar_chat(
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
