from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies.permissions import exigir_perfis
from app.schemas.UsuarioContexto import UsuarioContexto
from app.services.ordensServico.buscarOrdensServico import (
    consultar_minhas_ordens_servico,
)


router = APIRouter(
    prefix="/ordens-servico",
    tags=["Ordens de serviço"],
)


@router.get("/me")
async def consultar_minhas_ordens(
    usuario: Annotated[
        UsuarioContexto,
        Depends(exigir_perfis("tecnico", "gestor")),
    ],
) -> dict:
    return await consultar_minhas_ordens_servico(
        usuario.access_token,
    )