import asyncio
from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.graph import runner
from app.schemas.UsuarioContexto import UsuarioContexto


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


def test_executar_grafo_inicializa_estado_e_contexto(
    monkeypatch,
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
        runner,
        "grafo",
        grafo_mock,
    )

    monkeypatch.setattr(
        runner,
        "documento_id_da_sessao",
        AsyncMock(return_value="documento-123"),
    )
    monkeypatch.setattr(
        runner,
        "recuperar_mensagens",
        AsyncMock(return_value=[]),
    )
    salvar_mensagem = AsyncMock()
    monkeypatch.setattr(
        runner,
        "salvar_mensagem",
        salvar_mensagem,
    )

    usuario = criar_usuario()
    mensagem = "Como acompanho uma solicitacao?"

    resultado = asyncio.run(
        runner.executar_grafo(
            mensagem=mensagem,
            usuario=usuario,
            thread_id="conversa-123",
            imagens=["https://exemplo.com/imagem.jpg"],
        )
    )

    assert resultado["resposta_final"] == "Resposta de teste"

    argumentos, nomeados = ainvoke.await_args

    estado = argumentos[0]

    assert estado["user_id"] == "10"
    assert estado["perfil"] == "solicitante"
    assert estado["tentativas"] == 0
    assert estado["mensagem_anonimizada"] == mensagem
    assert estado["mapa_pii"] == {}
    assert estado["messages"][0].content == mensagem

    assert nomeados["config"] == {
        "configurable": {
            "thread_id": "10:conversa-123",
        }
    }

    assert nomeados["context"]["usuario"] == usuario
    assert nomeados["context"]["imagens"] == [
        "https://exemplo.com/imagem.jpg"
    ]

    assert salvar_mensagem.await_count == 2
