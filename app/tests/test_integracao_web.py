import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.api.dependencies.auth import obter_usuario_atual
from app.main import app
from app.schemas import UsuarioContexto
from app.services.gerais import perfil_web
from app.services import historico_web
from app.core import configuracao


def usuario():
    return UsuarioContexto(access_token="token-teste", usuario_id=12, nome_completo="Gestor Local",
                          email="gestor@fixa.test", tipo_acesso="gestor", cnpj_endereco="12345678000195")


def test_perfil_enum_objeto_resolve_unidade_pelo_usuario_validado(monkeypatch):
    consultar = AsyncMock(return_value=[{"cnpj": "12345678000195"}])
    monkeypatch.setattr(perfil_web, "executar_consulta", consultar)
    resultado = asyncio.run(perfil_web.completar_perfil({"id": 12, "tipoAcesso": {"id": 2, "nome": "Gestor"}}))
    assert resultado["tipoAcesso"] == "gestor"
    assert resultado["cnpjUnidade"] == "12345678000195"
    args = consultar.await_args.args
    assert args[0] == "gestor"
    assert "usuario.esta_ativo IS TRUE" in args[1]
    assert args[2] == {"usuario_id": 12}


def test_perfil_legado_preserva_cnpj_e_nao_consulta_banco(monkeypatch):
    consultar = AsyncMock()
    monkeypatch.setattr(perfil_web, "executar_consulta", consultar)
    resultado = asyncio.run(perfil_web.completar_perfil({"id": 12, "tipoAcesso": "TÉCNICO", "cnpjUnidade": "12345678000195"}))
    assert resultado["tipoAcesso"] == "tecnico"
    consultar.assert_not_awaited()


def test_perfil_sem_unidade_ativa_e_administrador_nao_recebem_acesso(monkeypatch):
    consultar = AsyncMock(return_value=[])
    monkeypatch.setattr(perfil_web, "executar_consulta", consultar)
    with pytest.raises(HTTPException) as erro:
        asyncio.run(perfil_web.completar_perfil({"id": 12, "tipoAcesso": "GESTOR"}))
    assert erro.value.status_code == 403
    with pytest.raises(HTTPException) as erro:
        asyncio.run(perfil_web.completar_perfil({"id": 12, "tipoAcesso": "ADMINISTRADOR"}))
    assert erro.value.status_code == 403
    assert consultar.await_count == 1


def test_historico_filtra_usuario_e_nao_expoe_campos_internos(monkeypatch):
    data = datetime.now(timezone.utc)
    documento = {"session_id": "thread-1", "user_id": 12, "iniciada_em": data, "atualizada_em": data,
                 "confirmacao": "sim", "access_token": "nao-expor", "solicitacao_pendente": {"segredo": "nao-expor"},
                 "mensagens": [{"role": "human", "content": "Olá"}, {"role": "assistant", "content": "Proposta", "emocao": "CONFIRMACAO"}]}
    consultar = AsyncMock(side_effect=lambda filtro, projection: documento if filtro == {"user_id": 12, "session_id": "thread-1"} else None)
    class Colecao:
        find_one = consultar
    class Banco:
        def __getitem__(self, key): return Colecao()
    class Cliente:
        def __getitem__(self, key): return Banco()
    @asynccontextmanager
    async def abrir(): yield Cliente()
    monkeypatch.setattr(historico_web, "abrir_cliente_mongo", abrir)
    historico = asyncio.run(historico_web.obter_conversa_web("thread-1", 12))
    assert historico.confirmacao == "sim"
    assert historico.messages[0].author == "user"
    assert historico.messages[1].author == "manu"
    assert "nao-expor" not in historico.model_dump_json()
    with pytest.raises(HTTPException) as erro:
        asyncio.run(historico_web.obter_conversa_web("thread-1", 99))
    assert erro.value.status_code == 404


def test_historico_exige_bearer_e_chat_sem_chaves_retorna_503(monkeypatch):
    cliente = TestClient(app)
    app.dependency_overrides.clear()
    assert cliente.get("/api/v1/chat/sessions").status_code == 401
    app.dependency_overrides[obter_usuario_atual] = usuario
    monkeypatch.setattr(configuracao, "OPENAI_CHAVE_API", None)
    monkeypatch.setattr(configuracao, "TYPESAFE_API_KEY", None)
    monkeypatch.setattr(configuracao, "GEMINI_CHAVE_API", None)
    try:
        resposta = cliente.post("/api/v1/chat", json={"mensagem": "Olá"})
    finally:
        app.dependency_overrides.clear()
    assert resposta.status_code == 503
    assert "OPENAI_API_KEY" in resposta.json()["detail"]


def test_cors_permite_origem_local_e_bearer():
    resposta = TestClient(app).options("/api/v1/chat", headers={
        "Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "authorization,content-type",
    })
    assert resposta.status_code == 200
    assert resposta.headers["access-control-allow-origin"] == "http://localhost:5173"
