"""Regressoes do resumo gerado ao encerrar uma sessao."""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from importlib import import_module
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from langchain_core.messages import AIMessage


@pytest.mark.parametrize("conteudo,esperado", [
    ("  Resumo da conversa.  ", "Resumo da conversa."),
    ([{"type": "reasoning", "reasoning": "interno"},
      {"type": "text", "text": "  Resumo da conversa.  "}], "Resumo da conversa."),
])
def test_gerar_resumo_aceita_texto_e_blocos(monkeypatch, conteudo, esperado):
    modulo = import_module("app.memory.persistencia.gerar_resumo")
    modelo = SimpleNamespace(ainvoke=AsyncMock(return_value=AIMessage(content=conteudo)))
    monkeypatch.setattr(modulo, "llm_rapido", modelo)

    resultado = asyncio.run(modulo.gerar_resumo([
        {"role": "human", "content": "Oi"},
    ]))

    assert resultado == esperado
    modelo.ainvoke.assert_awaited_once()


def test_encerramento_sem_texto_nao_tenta_gerar_embedding(monkeypatch):
    resumo = import_module("app.memory.persistencia.gerar_resumo")
    encerramento = import_module("app.memory.persistencia.sessoes.encerramento")
    monkeypatch.setattr(resumo, "llm_rapido", SimpleNamespace(
        ainvoke=AsyncMock(return_value=AIMessage(content=[
            {"type": "reasoning", "reasoning": "interno"},
        ])),
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
        update_one=AsyncMock(),
    )

    @asynccontextmanager
    async def abrir_mongo():
        yield {encerramento.MONGO_BANCO_DADOS: {
            encerramento.MONGO_COLECAO_SESSOES: colecao,
        }}

    monkeypatch.setattr(encerramento, "abrir_cliente_mongo", abrir_mongo)
    gerar_vetor = AsyncMock()
    monkeypatch.setattr(encerramento, "gerar_vetor_documento", gerar_vetor)

    resultado = asyncio.run(encerramento.encerrar_sessao("sessao", 7))

    assert resultado == ""
    assert colecao.update_one.await_args.args[1]["$set"]["resumo"] == ""
    assert (7, "sessao") not in encerramento.sessoes_ativas
    gerar_vetor.assert_not_awaited()
