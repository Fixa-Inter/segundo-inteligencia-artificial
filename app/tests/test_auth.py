import asyncio
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.api.dependencies import auth


def test_obter_usuario_atual(
    monkeypatch,
) -> None:
    consultar_perfil = AsyncMock(
        return_value={
            "id": 10,
            "nomeCompleto": "Usuário Teste",
            "email": "usuario@teste.com",
            "tipoAcesso": "SOLICITANTE",
            "cargo": "Solicitante",
            "dataNascimento": "2000-01-01",
            "cnpjEndereco": "12.345.678/0001-90",
        }
    )

    monkeypatch.setattr(
        auth,
        "consultar_perfil",
        consultar_perfil,
    )

    credenciais = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="token-teste",
    )

    usuario = asyncio.run(
        auth.obter_usuario_atual(credenciais)
    )

    assert usuario.usuario_id == 10
    assert usuario.tipo_acesso == "SOLICITANTE"
    assert usuario.cnpj_endereco == "12345678000190"
    assert usuario.access_token == "token-teste"


def test_obter_usuario_sem_token() -> None:
    with pytest.raises(HTTPException) as erro:
        asyncio.run(
            auth.obter_usuario_atual(None)
        )

    assert erro.value.status_code == 401