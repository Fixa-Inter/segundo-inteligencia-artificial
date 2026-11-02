from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from pydantic import ValidationError

from app.schemas import UsuarioContexto
from app.services.gerais.perfil import (
    ErroConsultaPerfil,
    consultar_perfil,
)

from app.core.respostas import MENSAGENS


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
            detail=MENSAGENS['token_de_acesso_nao_informado'],
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if credenciais.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=MENSAGENS['esquema_de_autenticacao_invalido'],
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
            cnpj_endereco=perfil["cnpjUnidade"],
        )

    except (KeyError, TypeError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                MENSAGENS['a_api_fixa_retornou_dados_de_perfil_incompativeis']
            ),
        ) from None
