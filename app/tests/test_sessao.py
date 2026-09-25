from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.api.dependencies.auth import obter_usuario_atual
from app.main import app
from app.schemas.UsuarioContexto import UsuarioContexto
from app.schemas.sessao import EncerrarSessaoResponse


client = TestClient(app)


def criar_usuario_teste() -> UsuarioContexto:
    return UsuarioContexto(
        access_token="token-teste",
        usuario_id=123,
        nome_completo="Usuário Teste",
        email="usuario@teste.com",
        tipo_acesso="solicitante",
        cargo="Analista",
        data_nascimento=None,
        cnpj_endereco="12345678000199",
    )


def test_encerrar_sessao_com_sucesso(monkeypatch):
    usuario = criar_usuario_teste()

    async def substituir_usuario_atual() -> UsuarioContexto:
        return usuario

    finalizar_sessao_mock = AsyncMock(
        return_value=EncerrarSessaoResponse(
            thread_id="conversa-123",
            status="ENCERRADA",
            mensagem="Sessão encerrada com sucesso.",
            resumo="Resumo da conversa.",
        )
    )

    # Substitui a autenticação real
    app.dependency_overrides[obter_usuario_atual] = substituir_usuario_atual

    # Substitui o serviço real para o teste não acessar memória ou banco
    monkeypatch.setattr(
        "app.api.routes.chat.finalizar_sessao_chat",
        finalizar_sessao_mock,
    )

    try:
        response = client.delete(
            "/api/v1/chat/sessions/conversa-123"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "thread_id": "conversa-123",
        "status": "ENCERRADA",
        "mensagem": "Sessão encerrada com sucesso.",
        "resumo": "Resumo da conversa.",
    }

    finalizar_sessao_mock.assert_awaited_once_with(
        thread_id="conversa-123",
        usuario=usuario,
    )


def test_encerrar_sessao_sem_autenticacao():
    app.dependency_overrides.clear()

    response = client.delete(
        "/api/v1/chat/sessions/conversa-123"
    )

    assert response.status_code == 401


def test_encerrar_sessao_com_thread_id_muito_longo():
    usuario = criar_usuario_teste()

    async def substituir_usuario_atual() -> UsuarioContexto:
        return usuario

    app.dependency_overrides[obter_usuario_atual] = substituir_usuario_atual

    try:
        thread_id_invalido = "a" * 101

        response = client.delete(
            f"/api/v1/chat/sessions/{thread_id_invalido}"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
