from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies.auth import obter_usuario_atual
from app.schemas.UsuarioContexto import UsuarioContexto
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat import processar_chat


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