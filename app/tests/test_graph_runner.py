import asyncio
from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.graph import executor
from app.schemas import UsuarioContexto


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
        )
    )

    assert resultado["resposta_final"] == "Resposta de teste"

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
    assert nomeados["context"]["imagens"] == [
        "https://exemplo.com/imagem.jpg"
    ]

    assert salvar_mensagem.await_count == 2
