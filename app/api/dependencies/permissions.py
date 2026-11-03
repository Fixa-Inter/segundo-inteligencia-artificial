from collections.abc import Callable
from typing import Annotated
from fastapi import Depends, HTTPException, status
from app.api.dependencies import obter_usuario_atual
from app.schemas import UsuarioContexto
from app.core import MENSAGENS

def exigir_perfis(
    *perfis_permitidos: str,
) -> Callable:
    """Cria dependência FastAPI que restringe acesso ao conjunto de perfis informado. Usado pelo fluxo de dependencies."""
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
        """Executa a etapa verificar perfil no escopo de permissions. Usado pelo fluxo de dependencies."""
        perfil_atual = usuario.tipo_acesso.strip().lower()

        if perfil_atual not in perfis_normalizados:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=MENSAGENS['usuario_sem_permissao_para_esta_operacao'],
            )

        return usuario

    return verificar_perfil
