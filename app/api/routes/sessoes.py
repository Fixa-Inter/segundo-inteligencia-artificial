from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.auth import obter_usuario_atual
from app.schemas import UsuarioContexto
from app.services.visualizacoes import PERFIS_VISUALIZACOES
from app.schemas.id_sessao import IdSessaoCaminho
from app.schemas.sessao import (
    ConversaEspecificaEntrada,
    ConversaEspecificaSaida,
    TodasConversasSaida,
    ExcluirConversaSaida,
)
from app.services.sessoes import (
    ErroConsultaHistorico,
    buscar_conversa,
    buscar_conversas_usuario,
    excluir_conversa,
)

from app.core.respostas import MENSAGENS


router = APIRouter(prefix="/sessoes", tags=["Sessões"])


def _traduzir_erro(erro: ErroConsultaHistorico) -> HTTPException:
    return HTTPException(status_code=erro.status_code, detail=erro.mensagem)


@router.get("", response_model=TodasConversasSaida)
async def pegar_todas_conversas_usuario(
    usuario: Annotated[UsuarioContexto, Depends(obter_usuario_atual)],
) -> TodasConversasSaida:
    try:
        conversas = await buscar_conversas_usuario(
            usuario.usuario_id, incluir_visualizacoes=usuario.tipo_acesso.strip().lower() in PERFIS_VISUALIZACOES,
        )
    except ErroConsultaHistorico as erro:
        raise _traduzir_erro(erro) from erro

    if not conversas:
        return TodasConversasSaida(
            status="SEM_DADOS",
            mensagem=MENSAGENS['voce_ainda_nao_possui_conversas_salvas'],
            conversas=[],
        )

    return TodasConversasSaida(
        status="SUCESSO",
        mensagem=MENSAGENS['conversas_carregadas_com_sucesso'],
        conversas=conversas,
    )


@router.post(
    "/conversa",
    response_model=ConversaEspecificaSaida,
)
async def pegar_conversa_especifica(
    dados: ConversaEspecificaEntrada,
    usuario: Annotated[UsuarioContexto, Depends(obter_usuario_atual)],
) -> ConversaEspecificaSaida:
    try:
        conversa = await buscar_conversa(
            session_id=dados.session_id,
            usuario_id=usuario.usuario_id,
            incluir_visualizacoes=usuario.tipo_acesso.strip().lower() in PERFIS_VISUALIZACOES,
        )
    except ErroConsultaHistorico as erro:
        raise _traduzir_erro(erro) from erro

    if conversa is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=MENSAGENS['a_conversa_solicitada_nao_foi_encontrada'],
        )

    return ConversaEspecificaSaida(
        status="SUCESSO",
        mensagem=MENSAGENS['conversa_carregada_com_sucesso'],
        conversa=conversa,
    )

@router.delete(
    "/conversa/{session_id}",
    response_model=ExcluirConversaSaida,
)
async def excluir_conversa_historico(
    session_id: IdSessaoCaminho,
    usuario: Annotated[
        UsuarioContexto,
        Depends(obter_usuario_atual),
    ],
) -> ExcluirConversaSaida:
    try:
        excluida = await excluir_conversa(
            session_id=session_id,
            usuario_id=usuario.usuario_id,
        )
    except ErroConsultaHistorico as erro:
        raise _traduzir_erro(erro) from erro

    if not excluida:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=MENSAGENS['a_conversa_solicitada_nao_foi_encontrada'],
        )

    return ExcluirConversaSaida(
        session_id=session_id,
        status="EXCLUIDA",
        mensagem=MENSAGENS['conversa_removida_do_historico'],
    )
