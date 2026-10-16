from fastapi.testclient import TestClient

from app.main import app


cliente = TestClient(app)


def test_health_check() -> None:
    resposta = cliente.get("/api/v1/health")

    assert resposta.status_code == 200
    assert resposta.json() == {
        "status": "ok",
        "service": "segundo-inteligencia-artificial",
    }