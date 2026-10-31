import asyncio
from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.graph import executor
from app.schemas import UsuarioContexto


@pytest.fixture(autouse=True)
def dependencias_persistencia(monkeypatch):
    monkeypatch.setattr(executor, "obter_analise_compra", AsyncMock(return_value=None))
    monkeypatch.setattr(executor, "obter_quantidade_anexos_pendentes", AsyncMock(return_value=0))


def criar_usuario() -> UsuarioContexto:
    return UsuarioContexto(
        access_token="token-teste",
        usuario_id=10,
        nome_completo="Usuário Teste",
        email="usuario@teste.com",
        tipo_acesso="solicitante",
        cargo="Solicitante",
        data_nascimento=date(2000, 1, 1),
        cnpj_endereco="12345678000190",
    )


@pytest.mark.parametrize("plataforma", ["web", "mobile"])
def test_executar_grafo_inicializa_estado_e_contexto(
    monkeypatch, plataforma,
) -> None:
    ainvoke = AsyncMock(
        return_value={
            "resposta_final": "Resposta de teste",
        }
    )

    grafo_mock = SimpleNamespace(
        ainvoke=ainvoke,
        get_state=lambda _: SimpleNamespace(values={}),
    )

    monkeypatch.setattr(
        executor,
        "grafo",
        grafo_mock,
    )

    monkeypatch.setattr(
        executor,
        "obter_documento_sessao_id",
        AsyncMock(return_value="documento-123"),
    )
    monkeypatch.setattr(
        executor,
        "recuperar_mensagens",
        AsyncMock(return_value=[]),
    )
    monkeypatch.setattr(executor, "obter_rascunho_solicitacao", AsyncMock(return_value=None))
    monkeypatch.setattr(executor, "obter_acao", AsyncMock(return_value=None))
    salvar_mensagem = AsyncMock()
    monkeypatch.setattr(
        executor,
        "salvar_mensagem",
        salvar_mensagem,
    )

    usuario = criar_usuario()
    mensagem = "Como acompanho uma solicitacao?"

    resultado = asyncio.run(
        executor.executar_grafo(
            mensagem=mensagem,
            usuario=usuario,
            thread_id="conversa-123",
            imagens=["https://exemplo.com/imagem.jpg"],
            plataforma=plataforma,
        )
    )

    assert resultado["resposta_final"] == "Resposta de teste"
    assert resultado["confirmacao"] == "nao"

    argumentos, nomeados = ainvoke.await_args

    estado = argumentos[0]

    assert estado["user_id"] == 10
    assert estado["perfil"] == "solicitante"
    assert estado["tentativas"] == 0
    assert estado["mensagem_anonimizada"] == mensagem
    assert estado["mapa_pii"] == {}
    assert estado["messages"][0].content == mensagem

    assert nomeados["config"]["configurable"] == {"thread_id": "10:conversa-123"}
    assert len(nomeados["config"]["callbacks"]) == 1

    assert nomeados["context"]["usuario"] == usuario
    assert nomeados["context"]["plataforma"] == plataforma
    assert nomeados["context"]["imagens"] == [
        "https://exemplo.com/imagem.jpg"
    ]

    assert salvar_mensagem.await_count == 2


@pytest.mark.parametrize("resposta_final", ["", " \t\n "])
def test_resposta_vazia_nao_e_persistida(monkeypatch, resposta_final) -> None:
    monkeypatch.setattr(executor, "grafo", SimpleNamespace(
        get_state=lambda _: SimpleNamespace(values={}),
        ainvoke=AsyncMock(return_value={"resposta_final": resposta_final}),
    ))
    monkeypatch.setattr(executor, "obter_documento_sessao_id", AsyncMock(return_value="documento"))
    monkeypatch.setattr(executor, "recuperar_mensagens", AsyncMock(return_value=[]))
    monkeypatch.setattr(executor, "obter_rascunho_solicitacao", AsyncMock(return_value=None))
    monkeypatch.setattr(executor, "obter_acao", AsyncMock(return_value=None))
    salvar_mensagem = AsyncMock()
    monkeypatch.setattr(executor, "salvar_mensagem", salvar_mensagem)
    atualizar_proposta = AsyncMock()
    monkeypatch.setattr(executor, "atualizar_rascunho_solicitacao", atualizar_proposta)

    with pytest.raises(HTTPException) as erro:
        asyncio.run(executor.executar_grafo("Minha dúvida", criar_usuario(), "conversa-123"))

    assert erro.value.status_code == 502
    assert "mensagem foi preservada" in erro.value.detail
    assert salvar_mensagem.await_count == 1
    assert salvar_mensagem.await_args.args[1] == "human"
    atualizar_proposta.assert_not_awaited()
