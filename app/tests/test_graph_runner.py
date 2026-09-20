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
        gerente_id=1,
        endereco_id=5,
        nome_completo="Usuário Teste",
        tipo_acesso="solicitante",
        cargo="Solicitante",
        data_nascimento=date(2000, 1, 1),
        esta_ativo=True,
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
    )

    monkeypatch.setattr(
        runner,
        "grafo",
        grafo_mock,
    )

    usuario = criar_usuario()

    resultado = asyncio.run(
        runner.executar_grafo(
            mensagem="Como acompanho uma solicitação?",
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
    assert estado["messages"][0].content == (
        "Como acompanho uma solicitação?"
    )

    assert nomeados["config"] == {
        "configurable": {
            "thread_id": "10:conversa-123",
        }
    }

    assert nomeados["context"]["usuario"] == usuario
    assert nomeados["context"]["imagens"] == [
        "https://exemplo.com/imagem.jpg"
    ]