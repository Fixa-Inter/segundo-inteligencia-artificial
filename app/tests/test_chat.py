from datetime import date
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.auth import obter_usuario_atual
from app.main import app
from app.schemas import UsuarioContexto
from app.schemas.chat import ConversaSaida


cliente = TestClient(app)


def usuario_teste(perfil: str = "solicitante") -> UsuarioContexto:
    return UsuarioContexto(
        access_token="token-teste",
        usuario_id=10,
        nome_completo="Usuário Teste",
        email="usuario@teste.com",
        tipo_acesso=perfil,
        cargo="Solicitante",
        data_nascimento=date(2000, 1, 1),
        cnpj_endereco="12345678000190",
    )


@pytest.mark.parametrize("perfil", ["solicitante", "administrador"])
def test_chat(monkeypatch, perfil) -> None:
    async def substituir_usuario():
        return usuario_teste(perfil)

    processar = AsyncMock(
        return_value=ConversaSaida(
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
        resposta = cliente.post(
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
        "emocao": "NEUTRO",
        "confirmacao": "nao",
    }
    assert processar.await_args.kwargs["usuario"].tipo_acesso == perfil


@pytest.mark.parametrize("resposta_final", ["", "   ", "\t\n"])
def test_chat_rejeita_resposta_vazia_sem_reenvio(monkeypatch, resposta_final) -> None:
    async def substituir_usuario():
        return usuario_teste()

    executar = AsyncMock(return_value={"resposta_final": resposta_final})
    monkeypatch.setattr("app.services.chat.sessao_acessivel", AsyncMock(return_value=True))
    monkeypatch.setattr("app.services.chat.executar_grafo", executar)
    app.dependency_overrides[obter_usuario_atual] = substituir_usuario

    try:
        resposta = cliente.post(
            "/api/v1/chat",
            json={"mensagem": "Como acompanho?", "thread_id": "conversa-1", "imagens": []},
        )
    finally:
        app.dependency_overrides.clear()

    assert resposta.status_code == 502
    assert "Manu não conseguiu gerar uma resposta" in resposta.json()["detail"]
    executar.assert_awaited_once()
