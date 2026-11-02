"""Horário de persistência em cada mensagem e nos contratos de histórico."""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from importlib import import_module
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from bson import BSON
from fastapi.testclient import TestClient

from app.main import app
from app.api.dependencies.auth import obter_usuario_atual
from app.schemas import UsuarioContexto
from app.schemas.sessao import MensagemHistorico

salvar = import_module("app.memory.persistencia.salvar_mensagem")
historico = import_module("app.services.sessoes.historico")


@pytest.mark.parametrize("papel", ["human", "assistant"])
def test_timestamp_e_instante_da_gravacao_e_atualizacao_da_sessao(monkeypatch, papel):
    instante = datetime(2026, 11, 1, 20, 30, 15, 123000, tzinfo=timezone.utc)
    colecao = SimpleNamespace(update_one=AsyncMock())

    @asynccontextmanager
    async def mongo():
        yield {salvar.MONGO_BANCO_DADOS: {salvar.MONGO_COLECAO_SESSOES: colecao}}

    monkeypatch.setattr(salvar, "abrir_cliente_mongo", mongo)
    monkeypatch.setattr(salvar, "obter_documento_sessao_id", AsyncMock(return_value="documento"))
    monkeypatch.setattr(salvar, "agora", Mock(return_value=instante))
    asyncio.run(salvar.salvar_mensagem("sessao", papel, "Mensagem", 7))
    atualizacao = colecao.update_one.await_args.args[1]
    assert atualizacao["$push"]["mensagens"]["timestamp"] == instante
    assert atualizacao["$set"]["atualizada_em"] == instante
    salvar.agora.assert_called_once()


@pytest.mark.parametrize("instante", [
    datetime(2026, 11, 1, 20, 30),
    datetime(2026, 11, 1, 17, 30, tzinfo=timezone(timedelta(hours=-3))),
    datetime(2026, 11, 1, 20, 30, tzinfo=timezone.utc),
])
def test_datas_bson_e_com_fuso_sao_expostas_em_utc(instante):
    mensagem = MensagemHistorico(role="human", mensagem="Teste", timestamp=instante)
    assert mensagem.model_dump(mode="json")["timestamp"] == "2026-11-01T20:30:00Z"


def test_mensagem_antiga_expoe_null_sem_inventar_data():
    formatada = historico._formatar_mensagens([{"role": "human", "content": "Antiga"}])[0]
    assert formatada["timestamp"] is None
    assert MensagemHistorico.model_validate(formatada).model_dump(mode="json")["timestamp"] is None


@pytest.mark.parametrize("rota", ["lista", "especifica"])
def test_endpoints_retornam_timestamps_reais_e_null_para_legados(monkeypatch, rota):
    inicio = datetime(2026, 11, 1, 20, 30, tzinfo=timezone.utc)
    documento = {"_id": "documento", "session_id": "sessao", "user_id": 7,
                 "iniciada_em": inicio, "atualizada_em": inicio, "titulo": "Teste", "resumo": "",
                 "mensagens": [{"role": "human", "content": "Mensagem antiga"}]}

    async def atualizar(filtro, operacao):
        assert filtro["user_id"] == 7
        documento["mensagens"].append(operacao["$push"]["mensagens"])
        documento.update(operacao["$set"])

    def ler_documento(*args, **kwargs):
        # O BSON perde tzinfo no retorno padrão do driver MongoDB.
        return BSON(BSON.encode(documento)).decode()

    cursor = SimpleNamespace(to_list=AsyncMock(side_effect=lambda **kwargs: [ler_documento()]))
    colecao = SimpleNamespace(update_one=atualizar, find_one=AsyncMock(side_effect=ler_documento),
                             find=Mock(return_value=SimpleNamespace(sort=lambda *args: cursor)))

    @asynccontextmanager
    async def mongo():
        yield {salvar.MONGO_BANCO_DADOS: {salvar.MONGO_COLECAO_SESSOES: colecao}}

    monkeypatch.setattr(salvar, "abrir_cliente_mongo", mongo)
    monkeypatch.setattr(historico, "abrir_cliente_mongo", mongo)
    monkeypatch.setattr(salvar, "obter_documento_sessao_id", AsyncMock(return_value="documento"))
    monkeypatch.setattr(salvar, "agora", Mock(side_effect=[inicio, inicio + timedelta(seconds=2)]))

    async def persistir():
        await salvar.salvar_mensagem("sessao", "human", "Nova pergunta", 7)
        await salvar.salvar_mensagem("sessao", "assistant", "Nova resposta", 7)

    asyncio.run(persistir())
    app.dependency_overrides[obter_usuario_atual] = lambda: UsuarioContexto.model_construct(usuario_id=7, tipo_acesso="gestor")
    try:
        cliente = TestClient(app)
        resposta = cliente.get("/api/v1/sessoes") if rota == "lista" else cliente.post(
            "/api/v1/sessoes/conversa", json={"session_id": "sessao"},
        )
    finally:
        app.dependency_overrides.clear()
    assert resposta.status_code == 200
    conversa = resposta.json()["conversas"][0] if rota == "lista" else resposta.json()["conversa"]
    assert [m["timestamp"] for m in conversa["mensagens"]] == [None, "2026-11-01T20:30:00Z", "2026-11-01T20:30:02Z"]
    assert documento["mensagens"][1]["timestamp"] != documento["mensagens"][2]["timestamp"]


def test_migracao_so_preenche_mensagens_sem_timestamp(monkeypatch):
    migracao = import_module("app.scripts.migrar_timestamps_mensagens")
    colecao = SimpleNamespace(update_many=AsyncMock(return_value=SimpleNamespace(modified_count=3)))

    @asynccontextmanager
    async def mongo():
        yield {migracao.MONGO_BANCO_DADOS: {migracao.MONGO_COLECAO_SESSOES: colecao}}

    monkeypatch.setattr(migracao, "abrir_cliente_mongo", mongo)
    assert asyncio.run(migracao.migrar_timestamps_mensagens()) == 3
    filtro, atualizacao = colecao.update_many.await_args.args
    assert filtro == {"mensagens": {"$elemMatch": {"timestamp": {"$exists": False}}}}
    assert atualizacao == {"$set": {"mensagens.$[mensagem].timestamp": None}}
    assert colecao.update_many.await_args.kwargs["array_filters"] == [{"mensagem.timestamp": {"$exists": False}}]
