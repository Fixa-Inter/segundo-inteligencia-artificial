from typing import Annotated
from app.api.dependencies import obter_usuario_atual
from app.schemas import UsuarioContexto, EncerrarSessaoSaida, ConversaEntrada, ConversaSaida, IdSessaoCaminho
from app.services import processar_chat, finalizar_sessao_chat
from fastapi import APIRouter, Depends, HTTPException, status

# router: Roteador HTTP que registra endpoints e contratos deste módulo.
router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


# Handler de chat que delega dados e usuário autenticado a processar_chat. Usado pelo fluxo de routes.
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


# Handler que encerra sessão própria e traduz erro de ID para HTTP 422. Usado pelo fluxo de routes.
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
