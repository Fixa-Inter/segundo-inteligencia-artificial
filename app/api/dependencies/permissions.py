from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.api.dependencies.auth import obter_usuario_atual
from app.schemas.UsuarioContexto import UsuarioContexto


def exigir_perfis(
    *perfis_permitidos: str,
) -> Callable:
    perfis_normalizados = {
        perfil.strip().lower()
        for perfil in perfis_permitidos
    }

    async def verificar_perfil(
        usuario: Annotated[
            UsuarioContexto,
            Depends(obter_usuario_atual),
        ],
    ) -> UsuarioContexto:
        perfil_atual = usuario.tipo_acesso.strip().lower()

        if perfil_atual not in perfis_normalizados:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário sem permissão para esta operação.",
            )

        return usuario

    return verificar_perfil