from datetime import date
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.api.dependencies.auth import obter_usuario_atual
from app.main import app
from app.schemas.UsuarioContexto import UsuarioContexto
from app.schemas.chat import ChatResponse


client = TestClient(app)


def usuario_teste() -> UsuarioContexto:
    return UsuarioContexto(
        access_token="token-teste",
        usuario_id=10,
        nome_completo="Usuário Teste",
        email="usuario@teste.com",
        tipo_acesso="solicitante",
        cargo="Solicitante",
        data_nascimento=date(2000, 1, 1),
        cnpj_endereco="12345678000190",
    )


def test_chat(monkeypatch) -> None:
    async def substituir_usuario():
        return usuario_teste()

    processar = AsyncMock(
        return_value=ChatResponse(
            thread_id="conversa-1",
            intencao="faq",
            resposta="Resposta de teste.",
        )
    )

    monkeypatch.setattr(
        "app.api.routes.chat.processar_chat",
        processar,
    )

    app.dependency_overrides[
        obter_usuario_atual
    ] = substituir_usuario

    try:
        resposta = client.post(
            "/api/v1/chat",
            json={
                "mensagem": "Como uso o aplicativo?",
                "thread_id": "conversa-1",
                "imagens": [],
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert resposta.status_code == 200
    assert resposta.json() == {
        "thread_id": "conversa-1",
        "intencao": "faq",
        "resposta": "Resposta de teste.",
    }