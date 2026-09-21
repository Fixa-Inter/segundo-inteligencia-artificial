from datetime import date
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.api.dependencies.auth import obter_usuario_atual
from app.main import app
from app.schemas.UsuarioContexto import UsuarioContexto


client = TestClient(app)


def usuario_teste() -> UsuarioContexto:
    return UsuarioContexto(
        access_token="token-teste",
        usuario_id=10,
        nome_completo="Gestor Teste",
        email="gestor@teste.com",
        tipo_acesso="gestor",
        cargo="Gestor",
        data_nascimento=date(1990, 1, 1),
        cnpj_endereco="12345678000190",
    )


def test_listar_meus_chamados(
    monkeypatch,
) -> None:
    async def substituir_usuario():
        return usuario_teste()

    servico = AsyncMock(
        return_value={
            "status": "SUCESSO",
            "solicitacoes": [],
            "mensagem": "Consulta concluída.",
        }
    )

    monkeypatch.setattr(
        "app.api.routes.chamados.listar_minhas_solicitacoes",
        servico,
    )

    app.dependency_overrides[
        obter_usuario_atual
    ] = substituir_usuario

    try:
        resposta = client.get(
            "/api/v1/chamados/me"
        )
    finally:
        app.dependency_overrides.clear()

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "SUCESSO"