from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.auth import obter_usuario_atual
from app.schemas import UsuarioContexto
from app.schemas.sessao import (
    ConversaEspecificaEntrada,
    ConversaEspecificaSaida,
    TodasConversasSaida,
)
from app.services.sessoes import (
    ErroConsultaHistorico,
    buscar_conversa,
    buscar_conversas_usuario,
)


router = APIRouter(prefix="/sessoes", tags=["Sessões"])


def _traduzir_erro(erro: ErroConsultaHistorico) -> HTTPException:
    return HTTPException(status_code=erro.status_code, detail=erro.mensagem)


@router.get("", response_model=TodasConversasSaida, response_model_exclude_none=True)
async def pegar_todas_conversas_usuario(
    usuario: Annotated[UsuarioContexto, Depends(obter_usuario_atual)],
) -> TodasConversasSaida:
    try:
        conversas = await buscar_conversas_usuario(usuario.usuario_id)
    except ErroConsultaHistorico as erro:
        raise _traduzir_erro(erro) from erro

    if not conversas:
        return TodasConversasSaida(
            status="SEM_DADOS",
            mensagem="Você ainda não possui conversas salvas.",
            conversas=[],
        )

    return TodasConversasSaida(
        status="SUCESSO",
        mensagem="Conversas carregadas com sucesso.",
        conversas=conversas,
    )


@router.post(
    "/conversa",
    response_model=ConversaEspecificaSaida,
    response_model_exclude_none=True,
)
async def pegar_conversa_especifica(
    dados: ConversaEspecificaEntrada,
    usuario: Annotated[UsuarioContexto, Depends(obter_usuario_atual)],
) -> ConversaEspecificaSaida:
    try:
        conversa = await buscar_conversa(
            session_id=dados.session_id,
            usuario_id=usuario.usuario_id,
        )
    except ErroConsultaHistorico as erro:
        raise _traduzir_erro(erro) from erro

    if conversa is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="A conversa solicitada não foi encontrada.",
        )

    return ConversaEspecificaSaida(
        status="SUCESSO",
        mensagem="Conversa carregada com sucesso.",
        conversa=conversa,
    )
