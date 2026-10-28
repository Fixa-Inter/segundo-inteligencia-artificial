from typing import Annotated

from app.api.dependencies.auth import obter_usuario_atual
from app.schemas import UsuarioContexto, EncerrarSessaoSaida
from app.schemas import ConversaEntrada, ConversaSaida
from app.services.chat import processar_chat
from app.services.sessao import finalizar_sessao_chat

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.id_sessao import IdSessaoCaminho

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post(
    "",
    response_model=ConversaSaida,
)
async def conversar(
    dados: ConversaEntrada,
    usuario: Annotated[
        UsuarioContexto,
        Depends(obter_usuario_atual),
    ],
) -> ConversaSaida:
    return await processar_chat(
        dados=dados,
        usuario=usuario,
    )


@router.delete(
    "/sessions/{thread_id}",
    response_model=EncerrarSessaoSaida,
)
async def encerrar_conversa(
    thread_id: IdSessaoCaminho,
    usuario: Annotated[
        UsuarioContexto,
        Depends(obter_usuario_atual),
    ],
) -> EncerrarSessaoSaida:
    try:
        return await finalizar_sessao_chat(
            thread_id=thread_id,
            usuario=usuario,
        )
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(erro),
        ) from erro
