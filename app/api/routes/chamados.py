from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies.auth import obter_usuario_atual
from app.api.dependencies.permissions import exigir_perfis
from app.schemas.UsuarioContexto import UsuarioContexto
from app.schemas.chamados import CriarChamadoRequest
from app.services.solicitacoes.buscarSolicitacao import (
    listar_minhas_solicitacoes,
    listar_solicitacoes_pendentes,
)
from app.services.solicitacoes.criarSolicitacao import (
    adicionar_solicitacao,
)
from app.tools.toolsRequest.CriarSolicitacaoRequest import (
    CriarSolicitacaoRequest,
)


router = APIRouter(
    prefix="/chamados",
    tags=["Chamados"],
)


@router.get("/me")
async def consultar_meus_chamados(
    usuario: Annotated[
        UsuarioContexto,
        Depends(obter_usuario_atual),
    ],
) -> dict:
    return await listar_minhas_solicitacoes(
        usuario.access_token,
    )


@router.get("/pendentes")
async def consultar_chamados_pendentes(
    usuario: Annotated[
        UsuarioContexto,
        Depends(exigir_perfis("gestor")),
    ],
) -> dict:
    return await listar_solicitacoes_pendentes(
        usuario.access_token,
    )


@router.post("")
async def criar_chamado(
    dados: CriarChamadoRequest,
    usuario: Annotated[
        UsuarioContexto,
        Depends(obter_usuario_atual),
    ],
) -> dict:
    solicitacao = CriarSolicitacaoRequest(
        categoria_equipamento_id=(
            dados.categoria_equipamento_id
        ),
        local_endereco_id=dados.local_endereco_id,
        titulo=dados.titulo,
        descricao_problema=dados.descricao_problema,
        descricao_local=dados.descricao_local,
    )

    return await adicionar_solicitacao(
        solicitacao=solicitacao,
        access_token=usuario.access_token,
        imagens=dados.imagens,
    )