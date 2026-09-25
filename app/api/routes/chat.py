from typing import Annotated

from app.api.dependencies.auth import obter_usuario_atual
from app.schemas.UsuarioContexto import UsuarioContexto
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat import processar_chat

from fastapi import APIRouter, Depends, Path

from app.schemas.sessao import (
    EncerrarSessaoResponse,
)
from app.services.sessao import (
    finalizar_sessao_chat,
)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
)
async def conversar(
    dados: ChatRequest,
    usuario: Annotated[
        UsuarioContexto,
        Depends(obter_usuario_atual),
    ],
) -> ChatResponse:
    return await processar_chat(
        dados=dados,
        usuario=usuario,
    )

@router.delete(
    "/sessions/{thread_id}",
    response_model=EncerrarSessaoResponse,
)
async def encerrar_conversa(
    thread_id: Annotated[
        str,
        Path(
            min_length=1,
            max_length=100,
        ),
    ],
    usuario: Annotated[
        UsuarioContexto,
        Depends(obter_usuario_atual),
    ],
) -> EncerrarSessaoResponse:
    return await finalizar_sessao_chat(
        thread_id=thread_id,
        usuario=usuario,
    )