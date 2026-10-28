"""Regressoes do resumo gerado ao encerrar uma sessao."""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from importlib import import_module
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient

from app.api.dependencies.auth import obter_usuario_atual
from app.main import app
from app.schemas import UsuarioContexto


def test_gerar_resumo_estruturado_valida_titulo_e_resumo(monkeypatch):
    modulo = import_module("app.memory.persistencia.gerar_resumo")
    modelo_estruturado = SimpleNamespace(ainvoke=AsyncMock(return_value={
        "titulo": "Teste de integração FIXA",
        "resumo": "O usuário realizou um teste de integração. A conversa registrou o resultado.",
    }))
    modelo = SimpleNamespace(with_structured_output=Mock(return_value=modelo_estruturado))
    monkeypatch.setattr(modulo, "llm_rapido", modelo)

    resultado = asyncio.run(modulo.gerar_resumo([
        {"role": "human", "content": "Oi"},
    ]))

    assert resultado.titulo == "Teste de integração FIXA"
    assert resultado.resumo == (
        "O usuário realizou um teste de integração. A conversa registrou o resultado."
    )
    modelo.with_structured_output.assert_called_once_with(
        modulo.ResumoGerado, method="json_schema"
    )
    modelo_estruturado.ainvoke.assert_awaited_once()


@pytest.mark.parametrize("titulo,resumo", [
    ("Um dois três quatro cinco seis sete oito nove dez onze", "Resumo válido."),
    ("Mesmo texto", "Mesmo texto"),
    ("", "Resumo válido."),
])
def test_gerar_resumo_rejeita_saida_invalida(monkeypatch, titulo, resumo):
    modulo = import_module("app.memory.persistencia.gerar_resumo")
    modelo = SimpleNamespace(with_structured_output=Mock(return_value=SimpleNamespace(
        ainvoke=AsyncMock(return_value={"titulo": titulo, "resumo": resumo}),
    )))
    monkeypatch.setattr(modulo, "llm_rapido", modelo)

    with pytest.raises(ValidationError):
        asyncio.run(modulo.gerar_resumo([{"role": "human", "content": "Oi"}]))


def test_falha_ao_gerar_resumo_nao_altera_sessao(monkeypatch):
    resumo = import_module("app.memory.persistencia.gerar_resumo")
    encerramento = import_module("app.memory.persistencia.sessoes.encerramento")
    monkeypatch.setattr(resumo, "llm_rapido", SimpleNamespace(
        with_structured_output=Mock(return_value=SimpleNamespace(
            ainvoke=AsyncMock(return_value={"titulo": "", "resumo": ""}),
        )),
    ))
    monkeypatch.setattr(encerramento, "obter_documento_sessao_id", AsyncMock(
        return_value="documento",
    ))
    monkeypatch.setattr(encerramento, "sessoes_ativas", {(7, "sessao"): "documento"})
    colecao = SimpleNamespace(
        find_one=AsyncMock(return_value={
            "mensagens": [{"role": "human", "content": "Oi"}],
            "iniciada_em": datetime.now(timezone.utc),
        }),
        update_one=AsyncMock(return_value=SimpleNamespace(matched_count=1)),
    )

    @asynccontextmanager
    async def abrir_mongo():
        yield {encerramento.MONGO_BANCO_DADOS: {
            encerramento.MONGO_COLECAO_SESSOES: colecao,
        }}

    monkeypatch.setattr(encerramento, "abrir_cliente_mongo", abrir_mongo)
    gerar_vetor = AsyncMock()
    monkeypatch.setattr(encerramento, "gerar_vetor_documento", gerar_vetor)

    with pytest.raises(ValidationError):
        asyncio.run(encerramento.encerrar_sessao("sessao", 7))

    colecao.update_one.assert_not_awaited()
    assert encerramento.sessoes_ativas[(7, "sessao")] == "documento"
    gerar_vetor.assert_not_awaited()


def test_encerramento_inexistente_nao_acessa_documento(monkeypatch):
    encerramento = import_module("app.memory.persistencia.sessoes.encerramento")
    buscar_id = AsyncMock(return_value=None)
    abrir_mongo = Mock()
    monkeypatch.setattr(encerramento, "obter_documento_sessao_id", buscar_id)
    monkeypatch.setattr(encerramento, "abrir_cliente_mongo", abrir_mongo)

    assert asyncio.run(encerramento.encerrar_sessao("inexistente", 7)) is None
    buscar_id.assert_awaited_once_with("inexistente", 7)
    abrir_mongo.assert_not_called()


def test_encerramento_de_outra_conta_nao_modifica_documento(monkeypatch):
    encerramento = import_module("app.memory.persistencia.sessoes.encerramento")
    monkeypatch.setattr(
        encerramento, "obter_documento_sessao_id",
        AsyncMock(return_value="documento-de-outra-conta"),
    )
    sessoes_ativas = {(7, "sessao-alheia"): "documento-de-outra-conta"}
    monkeypatch.setattr(encerramento, "sessoes_ativas", sessoes_ativas)

    async def buscar_documento(filtro):
        assert filtro == {
            "_id": "documento-de-outra-conta",
            "user_id": 8,
            "esta_ativo": True,
        }
        return None

    colecao = SimpleNamespace(
        find_one=AsyncMock(side_effect=buscar_documento),
        update_one=AsyncMock(),
    )

    @asynccontextmanager
    async def abrir_mongo():
        yield {encerramento.MONGO_BANCO_DADOS: {
            encerramento.MONGO_COLECAO_SESSOES: colecao,
        }}

    monkeypatch.setattr(encerramento, "abrir_cliente_mongo", abrir_mongo)
    gerar_resumo = AsyncMock()
    monkeypatch.setattr(encerramento, "gerar_resumo", gerar_resumo)

    assert asyncio.run(encerramento.encerrar_sessao("sessao-alheia", 8)) is None
    colecao.update_one.assert_not_awaited()
    gerar_resumo.assert_not_awaited()
    assert sessoes_ativas == {(7, "sessao-alheia"): "documento-de-outra-conta"}


def test_titulo_e_resumo_persistem_nas_duas_consultas_de_historico(monkeypatch):
    geracao = import_module("app.memory.persistencia.gerar_resumo")
    encerramento = import_module("app.memory.persistencia.sessoes.encerramento")
    historico = import_module("app.services.sessoes.historico")
    agora = datetime.now(timezone.utc)
    documento = {
        "_id": "00000000-0000-0000-0000-000000000007",
        "session_id": "sessao-qa",
        "user_id": 7,
        "esta_ativo": True,
        "iniciada_em": agora,
        "atualizada_em": agora,
        "titulo": "",
        "resumo": "",
        "mensagens": [{"role": "human", "content": "Teste de integração"}],
    }

    def projetar(projecao):
        if projecao is None:
            return documento.copy()
        return {
            chave: valor for chave, valor in documento.items()
            if projecao.get(chave, chave == "_id")
        }

    async def buscar(filtro, projecao=None, **_):
        if filtro.get("user_id") != 7 or not documento["esta_ativo"]:
            return None
        return projetar(projecao)

    async def atualizar(filtro, alteracao):
        assert filtro == {
            "_id": documento["_id"], "user_id": 7, "esta_ativo": True,
        }
        documento.update(alteracao["$set"])
        return SimpleNamespace(matched_count=1)

    class Cursor:
        def sort(self, *_):
            return self

        async def to_list(self, **_):
            return [projetar(historico._PROJECAO)]

    colecao = SimpleNamespace(
        find_one=AsyncMock(side_effect=buscar),
        update_one=AsyncMock(side_effect=atualizar),
        find=Mock(return_value=Cursor()),
    )

    @asynccontextmanager
    async def abrir_mongo():
        yield {encerramento.MONGO_BANCO_DADOS: {
            encerramento.MONGO_COLECAO_SESSOES: colecao,
        }}

    qdrant = SimpleNamespace(upsert=AsyncMock())

    @asynccontextmanager
    async def abrir_qdrant():
        yield qdrant

    monkeypatch.setattr(encerramento, "abrir_cliente_mongo", abrir_mongo)
    monkeypatch.setattr(historico, "abrir_cliente_mongo", abrir_mongo)
    monkeypatch.setattr(encerramento, "abrir_cliente_qdrant", abrir_qdrant)
    monkeypatch.setattr(
        encerramento, "obter_documento_sessao_id", AsyncMock(return_value=documento["_id"])
    )
    monkeypatch.setattr(encerramento, "sessoes_ativas", {})
    monkeypatch.setattr(encerramento, "gerar_vetor_documento", AsyncMock(return_value=[0.1]))
    gerado = geracao.ResumoGerado(
        titulo="Teste de integração FIXA",
        resumo="O usuário iniciou um teste de integração. A conversa registrou o resultado.",
    )
    monkeypatch.setattr(encerramento, "gerar_resumo", AsyncMock(return_value=gerado))

    resultado = asyncio.run(encerramento.encerrar_sessao("sessao-qa", 7))

    async def substituir_usuario_atual() -> UsuarioContexto:
        return UsuarioContexto(
            access_token="teste", usuario_id=7, nome_completo="Usuário Teste",
            email="usuario@teste.com", tipo_acesso="solicitante", cargo="Analista",
            data_nascimento=None, cnpj_endereco="12345678000199",
        )

    app.dependency_overrides[obter_usuario_atual] = substituir_usuario_atual
    try:
        cliente = TestClient(app)
        lista = cliente.get("/api/v1/sessoes")
        especifica = cliente.post(
            "/api/v1/sessoes/conversa", json={"session_id": "sessao-qa"}
        )
    finally:
        app.dependency_overrides.clear()

    assert resultado == gerado.model_dump()
    assert documento["titulo"] == gerado.titulo
    assert documento["resumo"] == gerado.resumo
    assert lista.status_code == 200
    assert especifica.status_code == 200
    assert lista.json()["conversas"][0]["titulo"] == gerado.titulo
    assert lista.json()["conversas"][0]["resumo"] == gerado.resumo
    assert especifica.json()["conversa"]["titulo"] == gerado.titulo
    assert especifica.json()["conversa"]["resumo"] == gerado.resumo
    qdrant.upsert.assert_awaited_once()


def test_historico_legado_nao_interpreta_primeira_linha_como_titulo():
    historico = import_module("app.services.sessoes.historico")
    documento = {
        "session_id": "legada",
        "iniciada_em": datetime.now(timezone.utc),
        "atualizada_em": datetime.now(timezone.utc),
        "resumo": "Primeira frase extensa.\nSegunda frase.",
        "mensagens": [],
    }

    conversa = historico._formatar_conversa(documento)

    assert conversa["titulo"] == ""
    assert conversa["resumo"] == documento["resumo"]
