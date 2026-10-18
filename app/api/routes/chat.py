from typing import Annotated

from app.api.dependencies.auth import obter_usuario_atual
from app.schemas import UsuarioContexto
from app.schemas import ConversaEntrada, ConversaSaida
from app.services.chat import processar_chat

from fastapi import APIRouter, Depends, Path

from app.schemas import (
    EncerrarSessaoSaida,
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
) -> EncerrarSessaoSaida:
    return await finalizar_sessao_chat(
        thread_id=thread_id,
        usuario=usuario,
    )