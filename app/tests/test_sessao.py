from contextlib import asynccontextmanager
from importlib import import_module
from unittest.mock import AsyncMock
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.auth import obter_usuario_atual
from app.main import app
from app.schemas import UsuarioContexto
from app.schemas import EncerrarSessaoSaida
from app.services import sessao as servico_sessao
from app.services import chat as servico_chat


cliente = TestClient(app)


def criar_usuario_teste() -> UsuarioContexto:
    return UsuarioContexto(
        access_token="token-teste",
        usuario_id=123,
        nome_completo="Usuário Teste",
        email="usuario@teste.com",
        tipo_acesso="solicitante",
        cargo="Analista",
        data_nascimento=None,
        cnpj_endereco="12345678000199",
    )


def test_encerrar_sessao_com_sucesso(monkeypatch):
    usuario = criar_usuario_teste()

    async def substituir_usuario_atual() -> UsuarioContexto:
        return usuario

    finalizar_sessao_mock = AsyncMock(
        return_value=EncerrarSessaoSaida(
            thread_id="conversa-123",
            status="ENCERRADA",
            mensagem="Sessão encerrada com sucesso.",
            titulo="Teste de integração FIXA",
            resumo="Resumo da conversa.",
        )
    )

    # Substitui a autenticação real
    app.dependency_overrides[obter_usuario_atual] = substituir_usuario_atual

    # Substitui o serviço real para o teste não acessar memória ou banco
    monkeypatch.setattr(
        "app.api.routes.chat.finalizar_sessao_chat",
        finalizar_sessao_mock,
    )

    try:
        resposta = cliente.delete(
            "/api/v1/chat/sessions/conversa-123"
        )
    finally:
        app.dependency_overrides.clear()

    assert resposta.status_code == 200
    assert resposta.json() == {
        "thread_id": "conversa-123",
        "status": "ENCERRADA",
        "mensagem": "Sessão encerrada com sucesso.",
        "titulo": "Teste de integração FIXA",
        "resumo": "Resumo da conversa.",
    }

    finalizar_sessao_mock.assert_awaited_once_with(
        thread_id="conversa-123",
        usuario=usuario,
    )


def test_encerrar_sessao_sem_autenticacao():
    app.dependency_overrides.clear()

    resposta = cliente.delete(
        "/api/v1/chat/sessions/conversa-123"
    )

    assert resposta.status_code == 401


@pytest.mark.parametrize(
    "thread_id,status_esperado",
    [("%20", 422), ("00000000-0000-4000-8000-000000000001", 404)],
)
def test_encerrar_com_bearer_valido_rejeita_id_invalido_ou_inexistente(
    monkeypatch, thread_id, status_esperado,
):
    auth = import_module("app.api.dependencies.auth")
    consultar_perfil = AsyncMock(return_value={
        "id": 123,
        "nomeCompleto": "Usuário Teste",
        "email": "usuario@teste.com",
        "tipoAcesso": "solicitante",
        "cnpjUnidade": "12345678000199",
    })
    encerrar = AsyncMock(return_value=None)
    monkeypatch.setattr(auth, "consultar_perfil", consultar_perfil)
    monkeypatch.setattr(servico_sessao, "encerrar_sessao", encerrar)
    app.dependency_overrides.clear()

    resposta = cliente.delete(
        f"/api/v1/chat/sessions/{thread_id}",
        headers={"Authorization": "Bearer token-qa-valido"},
    )

    assert resposta.status_code == status_esperado
    consultar_perfil.assert_awaited_once_with(access_token="token-qa-valido")
    if status_esperado == 422:
        encerrar.assert_not_awaited()
    else:
        encerrar.assert_awaited_once_with(sessao_id=thread_id, usuario_id=123)


@pytest.mark.parametrize(
    "rota",
    ["/api/v1/chat/sessions/", "/api/v1/sessoes/conversa/"],
)
def test_id_sessao_muito_longo_e_rejeitado(rota):
    usuario = criar_usuario_teste()

    async def substituir_usuario_atual() -> UsuarioContexto:
        return usuario

    app.dependency_overrides[obter_usuario_atual] = substituir_usuario_atual

    try:
        resposta = cliente.delete(rota + "a" * 101)
    finally:
        app.dependency_overrides.clear()

    assert resposta.status_code == 422


@pytest.mark.parametrize(
    "rota,servico",
    [
        ("/api/v1/chat/sessions/", "app.api.routes.chat.finalizar_sessao_chat"),
        ("/api/v1/sessoes/conversa/", "app.api.routes.sessoes.excluir_conversa"),
    ],
)
@pytest.mark.parametrize("id_codificado", ["%20", "%09", "%20%09%20"])
def test_id_sessao_em_branco_e_rejeitado_antes_do_servico(
    monkeypatch, rota, servico, id_codificado,
):
    async def substituir_usuario_atual() -> UsuarioContexto:
        return criar_usuario_teste()

    chamada = AsyncMock()
    app.dependency_overrides[obter_usuario_atual] = substituir_usuario_atual
    monkeypatch.setattr(servico, chamada)
    try:
        resposta = cliente.delete(rota + id_codificado)
    finally:
        app.dependency_overrides.clear()

    assert resposta.status_code == 422
    chamada.assert_not_awaited()


@pytest.mark.parametrize(
    "rota,servico,resultado",
    [
        (
            "/api/v1/chat/sessions/",
            "app.api.routes.chat.finalizar_sessao_chat",
            EncerrarSessaoSaida(
                thread_id="conversa-123", status="ENCERRADA", mensagem="Encerrada."
            ),
        ),
        (
            "/api/v1/sessoes/conversa/",
            "app.api.routes.sessoes.excluir_conversa",
            True,
        ),
    ],
)
def test_id_sessao_valido_e_normalizado_antes_do_servico(
    monkeypatch, rota, servico, resultado,
):
    usuario = criar_usuario_teste()

    async def substituir_usuario_atual() -> UsuarioContexto:
        return usuario

    chamada = AsyncMock(return_value=resultado)
    app.dependency_overrides[obter_usuario_atual] = substituir_usuario_atual
    monkeypatch.setattr(servico, chamada)
    try:
        resposta = cliente.delete(rota + "%20conversa-123%20")
    finally:
        app.dependency_overrides.clear()

    assert resposta.status_code == 200
    assert resposta.json()["thread_id" if "chat" in rota else "session_id"] == "conversa-123"
    chamada.assert_awaited_once_with(
        **{"thread_id" if "chat" in rota else "session_id": "conversa-123"},
        **({"usuario": usuario} if "chat" in rota else {"usuario_id": usuario.usuario_id}),
    )


def test_value_error_do_encerramento_vira_422(monkeypatch):
    async def substituir_usuario_atual() -> UsuarioContexto:
        return criar_usuario_teste()

    app.dependency_overrides[obter_usuario_atual] = substituir_usuario_atual
    monkeypatch.setattr(
        "app.api.routes.chat.finalizar_sessao_chat",
        AsyncMock(side_effect=ValueError("O thread_id não pode estar vazio.")),
    )
    try:
        resposta = cliente.delete("/api/v1/chat/sessions/conversa-123")
    finally:
        app.dependency_overrides.clear()

    assert resposta.status_code == 422


def test_consulta_sessao_em_branco_e_rejeitada_antes_do_servico(monkeypatch):
    async def substituir_usuario_atual() -> UsuarioContexto:
        return criar_usuario_teste()

    chamada = AsyncMock()
    app.dependency_overrides[obter_usuario_atual] = substituir_usuario_atual
    monkeypatch.setattr("app.api.routes.sessoes.buscar_conversa", chamada)
    try:
        resposta = cliente.post(
            "/api/v1/sessoes/conversa", json={"session_id": " \t "}
        )
    finally:
        app.dependency_overrides.clear()

    assert resposta.status_code == 422
    chamada.assert_not_awaited()


@pytest.mark.parametrize("thread_id", ["inexistente", "sessao-de-outra-conta"])
def test_encerrar_sessao_sem_acesso_retorna_404_uniforme(monkeypatch, thread_id):
    usuario = criar_usuario_teste()

    async def substituir_usuario_atual() -> UsuarioContexto:
        return usuario

    encerrar = AsyncMock(return_value=None)
    checkpointer = SimpleNamespace(adelete_thread=AsyncMock())
    monkeypatch.setattr(servico_sessao, "encerrar_sessao", encerrar)
    monkeypatch.setattr(servico_sessao, "grafo", SimpleNamespace(checkpointer=checkpointer))
    app.dependency_overrides[obter_usuario_atual] = substituir_usuario_atual
    try:
        resposta = cliente.delete(f"/api/v1/chat/sessions/{thread_id}")
    finally:
        app.dependency_overrides.clear()

    assert resposta.status_code == 404
    assert resposta.json() == {"detail": "Conversa não encontrada."}
    encerrar.assert_awaited_once_with(sessao_id=thread_id, usuario_id=usuario.usuario_id)
    checkpointer.adelete_thread.assert_not_awaited()


def test_encerrar_sessao_propria_persiste_resumo(monkeypatch):
    usuario = criar_usuario_teste()

    async def substituir_usuario_atual() -> UsuarioContexto:
        return usuario

    encerrar = AsyncMock(return_value={
        "titulo": "Teste de integração FIXA", "resumo": "Resumo da conversa.",
    })
    checkpointer = SimpleNamespace(adelete_thread=AsyncMock())
    monkeypatch.setattr(servico_sessao, "encerrar_sessao", encerrar)
    monkeypatch.setattr(servico_sessao, "grafo", SimpleNamespace(checkpointer=checkpointer))
    app.dependency_overrides[obter_usuario_atual] = substituir_usuario_atual
    try:
        resposta = cliente.delete("/api/v1/chat/sessions/conversa-123")
    finally:
        app.dependency_overrides.clear()

    assert resposta.status_code == 200
    assert resposta.json()["titulo"] == "Teste de integração FIXA"
    assert resposta.json()["resumo"] == "Resumo da conversa."
    encerrar.assert_awaited_once_with(sessao_id="conversa-123", usuario_id=usuario.usuario_id)
    checkpointer.adelete_thread.assert_awaited_once_with("123:conversa-123")


def test_conversa_encerrada_pode_continuar_ate_ser_excluida_do_historico(monkeypatch):
    usuario = criar_usuario_teste()
    documento = {
        "_id": "documento-qa",
        "user_id": usuario.usuario_id,
        "session_id": "conversa-qa",
        "esta_ativo": True,
        "mensagens": [],
    }

    def corresponde(filtro):
        return all(
            documento.get(campo) == valor
            for campo, valor in filtro.items()
        )

    async def buscar(filtro, projecao=None, **_):
        if not corresponde(filtro):
            return None
        if projecao is not None:
            return {campo: documento[campo] for campo in projecao if campo in documento}
        return documento.copy()

    async def atualizar(filtro, alteracao):
        if not corresponde(filtro):
            return SimpleNamespace(matched_count=0)
        documento.update(alteracao["$set"])
        return SimpleNamespace(matched_count=1)

    async def excluir(filtro, alteracao):
        if not corresponde(filtro):
            return SimpleNamespace(modified_count=0)
        documento.update(alteracao["$set"])
        return SimpleNamespace(modified_count=1)

    colecao = SimpleNamespace(find_one=buscar, update_one=atualizar, update_many=excluir)
    encerramento = import_module("app.memory.persistencia.sessoes.encerramento")
    utilitarios = import_module("app.memory.persistencia.utilitarios")
    historico = import_module("app.services.sessoes.historico")

    @asynccontextmanager
    async def abrir_mongo():
        yield {encerramento.MONGO_BANCO_DADOS: {
            encerramento.MONGO_COLECAO_SESSOES: colecao,
        }}

    monkeypatch.setattr(encerramento, "abrir_cliente_mongo", abrir_mongo)
    monkeypatch.setattr(utilitarios, "abrir_cliente_mongo", abrir_mongo)
    monkeypatch.setattr(historico, "abrir_cliente_mongo", abrir_mongo)
    monkeypatch.setattr(
        encerramento, "obter_documento_sessao_id",
        AsyncMock(return_value="documento-qa"),
    )
    monkeypatch.setattr(encerramento, "sessoes_ativas", {})
    monkeypatch.setattr(
        servico_sessao, "grafo",
        SimpleNamespace(checkpointer=SimpleNamespace(adelete_thread=AsyncMock())),
    )
    executar = AsyncMock(return_value={"resposta_final": "Pode continuar."})
    monkeypatch.setattr(servico_chat, "executar_grafo", executar)

    async def substituir_usuario_atual() -> UsuarioContexto:
        return usuario

    app.dependency_overrides[obter_usuario_atual] = substituir_usuario_atual
    try:
        encerrada = cliente.delete("/api/v1/chat/sessions/conversa-qa")
        continuacao = cliente.post(
            "/api/v1/chat",
            json={"mensagem": "Continuar", "thread_id": "conversa-qa"},
        )
        exclusao = cliente.delete("/api/v1/sessoes/conversa/conversa-qa")
        apos_exclusao = cliente.post(
            "/api/v1/chat",
            json={"mensagem": "Continuar", "thread_id": "conversa-qa"},
        )
    finally:
        app.dependency_overrides.clear()

    assert encerrada.status_code == 200
    assert continuacao.status_code == 200
    assert continuacao.json()["thread_id"] == "conversa-qa"
    assert exclusao.status_code == 200
    assert apos_exclusao.status_code == 404
    assert documento["esta_ativo"] is False
    executar.assert_awaited_once()
