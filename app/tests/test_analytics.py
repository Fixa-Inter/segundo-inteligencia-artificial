from datetime import date

from fastapi.testclient import TestClient

from app.api.dependencies.auth import obter_usuario_atual
from app.main import app
from app.schemas.UsuarioContexto import UsuarioContexto


client = TestClient(app)


def gestor_teste() -> UsuarioContexto:
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


def test_analytics_mockado() -> None:
    async def substituir_usuario():
        return gestor_teste()

    app.dependency_overrides[
        obter_usuario_atual
    ] = substituir_usuario

    try:
        resposta = client.post(
            "/api/v1/analytics/resumo",
            json={
                "inicio": "2026-09-01",
                "fim": "2026-09-30",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "DADOS_MOCKADOS"
    assert resposta.json()["fonte"] == "mock"
    assert resposta.json()["resultado"] is None