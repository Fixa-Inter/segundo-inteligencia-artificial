import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock

import httpx
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.api.dependencies import auth
from app.services.gerais import perfil


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
            "cnpjUnidade": "12.345.678/0001-90",
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
    assert usuario.tipo_acesso == "solicitante"
    assert usuario.cnpj_endereco == "12345678000190"
    assert usuario.access_token == "token-teste"


def test_obter_usuario_sem_token() -> None:
    with pytest.raises(HTTPException) as erro:
        asyncio.run(
            auth.obter_usuario_atual(None)
        )

    assert erro.value.status_code == 401


def test_consulta_perfil_segue_contrato_api(monkeypatch) -> None:
    contrato = json.loads(
        (Path(__file__).resolve().parents[2] / "docs/api/swagger.json")
        .read_text(encoding="utf-8")
    )
    dados = {
        "id": 10,
        "nomeCompleto": "Usuario Teste",
        "email": "usuario@teste.com",
        "tipoAcesso": "SOLICITANTE",
        "cnpjUnidade": "12.345.678/0001-90",
    }
    propriedades = contrato["components"]["schemas"]["UsuarioOutputDTO"]["properties"]
    assert set(dados) <= set(propriedades)
    assert "get" in contrato["paths"]["/api/v1/perfil"]

    requisicoes = []

    def responder(requisicao):
        requisicoes.append(requisicao)
        return httpx.Response(200, json=dados)

    fabrica_cliente = httpx.AsyncClient
    transporte = httpx.MockTransport(responder)
    monkeypatch.setattr(perfil, "FIXA_URL_BASE_API", "https://example.com/")
    monkeypatch.setattr(
        perfil.httpx,
        "AsyncClient",
        lambda **opcoes: fabrica_cliente(transport=transporte, **opcoes),
    )
    credenciais = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials="token-teste",
    )

    usuario = asyncio.run(auth.obter_usuario_atual(credenciais))

    assert usuario.cnpj_endereco == "12345678000190"
    assert len(requisicoes) == 1
    assert requisicoes[0].method == "GET"
    assert str(requisicoes[0].url) == "https://example.com/api/v1/perfil"
    assert requisicoes[0].headers["Authorization"] == "Bearer token-teste"
