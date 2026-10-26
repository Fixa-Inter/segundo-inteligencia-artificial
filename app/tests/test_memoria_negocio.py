"""Valida a persistência de sessão com uma coleção Mongo simulada."""

import asyncio
from contextlib import asynccontextmanager
from importlib import import_module
from types import SimpleNamespace
from unittest.mock import AsyncMock


def preparar_cliente(monkeypatch, modulo, colecao):
    @asynccontextmanager
    async def abrir():
        yield {modulo.MONGO_BANCO_DADOS: {modulo.MONGO_COLECAO_SESSOES: colecao}}

    monkeypatch.setattr(modulo, "abrir_cliente_mongo", abrir)


def test_salvar_mensagem_preserva_dono_e_anexos(monkeypatch):
    modulo = import_module("app.memory.persistencia.salvar_mensagem")
    colecao = SimpleNamespace(update_one=AsyncMock())
    preparar_cliente(monkeypatch, modulo, colecao)
    monkeypatch.setattr(modulo, "obter_documento_sessao_id", AsyncMock(return_value="documento"))
    anexar = AsyncMock()
    monkeypatch.setattr(modulo, "adicionar_imagens_sessao", anexar)
    asyncio.run(modulo.salvar_mensagem("sessao", "human", "Texto anônimo", 7,
                                      imagens=[" https://exemplo.com/foto.jpg ", ""]))
    filtro, atualizacao = colecao.update_one.await_args.args
    assert filtro == {"_id": "documento", "user_id": 7, "esta_ativo": True}
    assert atualizacao["$push"]["mensagens"] == {
        "role": "human", "content": "Texto anônimo", "imagens": ["https://exemplo.com/foto.jpg"],
    }
    anexar.assert_awaited_once_with(sessao_id="sessao", usuario_id=7,
                                   imagens=["https://exemplo.com/foto.jpg"])


def test_sessao_existente_nao_cria_segundo_documento(monkeypatch):
    modulo = import_module("app.memory.persistencia.sessoes.inicio")
    colecao = SimpleNamespace(insert_one=AsyncMock())
    preparar_cliente(monkeypatch, modulo, colecao)
    monkeypatch.setattr(modulo, "obter_documento_sessao_id", AsyncMock(return_value="existente"))
    asyncio.run(modulo.iniciar_sessao("sessao", 7))
    colecao.insert_one.assert_not_awaited()


def test_acao_somente_inicia_se_ainda_aguarda_confirmacao(monkeypatch):
    modulo = import_module("app.memory.persistencia.acao_ajuda_geral")
    colecao = SimpleNamespace(update_one=AsyncMock(return_value=SimpleNamespace(matched_count=1)))
    preparar_cliente(monkeypatch, modulo, colecao)
    monkeypatch.setattr(modulo, "obter_documento_sessao_id", AsyncMock(return_value="documento"))
    assert asyncio.run(modulo.iniciar_acao("sessao", 7, "proposta")) is True
    filtro, atualizacao = colecao.update_one.await_args.args
    assert filtro == {"_id": "documento", "user_id": 7, "esta_ativo": True,
                      "ajuda_geral_pendente.id": "proposta",
                      "ajuda_geral_pendente.status": "aguardando_confirmacao"}
    assert atualizacao["$set"]["ajuda_geral_pendente.status"] == "executando"
