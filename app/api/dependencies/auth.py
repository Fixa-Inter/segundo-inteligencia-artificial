from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from pydantic import ValidationError

from app.schemas.UsuarioContexto import UsuarioContexto
from app.services.gerais.perfil import (
    ErroConsultaPerfil,
    consultar_perfil,
)


bearer_scheme = HTTPBearer(
    auto_error=False,
)


async def obter_usuario_atual(
    credenciais: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
) -> UsuarioContexto:
    if credenciais is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acesso não informado.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if credenciais.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Esquema de autenticação inválido.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    access_token = credenciais.credentials

    try:
        perfil = await consultar_perfil(
            access_token=access_token,
        )

    except ErroConsultaPerfil as erro:
        raise HTTPException(
            status_code=erro.status_code,
            detail=erro.mensagem,
        ) from erro
    
    try:
        return UsuarioContexto(
            access_token=access_token,
            usuario_id=perfil["id"],
            nome_completo=perfil["nomeCompleto"],
            email=perfil["email"],
            tipo_acesso=perfil["tipoAcesso"],
            cargo=perfil.get("cargo"),
            data_nascimento=perfil.get("dataNascimento"),
            cnpj_endereco=perfil["cnpjEndereco"],
        )

    except (KeyError, TypeError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "A API FIXA retornou dados de perfil incompatíveis."
            ),
        ) from None