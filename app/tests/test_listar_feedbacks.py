import asyncio
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.schemas import UsuarioContexto
from app.services.feedback import listarFeedbacks as servico
from app.tools.feedback.listarFeedbacks import listar_meus_feedbacks


@pytest.mark.parametrize("perfil", ["solicitante", "tecnico", "gestor", "administrador"])
def test_listagem_usa_somente_id_autenticado_e_preserva_conteudo(monkeypatch, perfil):
    consulta = AsyncMock(return_value=[{"id": 1, "comentario": "Sugestão", "ideia_central": "Melhoria",
                                      "data_criacao": datetime(2026, 11, 2, 12)}])
    monkeypatch.setattr(servico, "executar_consulta", consulta)
    usuario = UsuarioContexto.model_construct(usuario_id=7, tipo_acesso=perfil)
    resultado = asyncio.run(listar_meus_feedbacks.coroutine(SimpleNamespace(context={"usuario": usuario})))
    assert resultado["status"] == "SUCESSO"
    assert resultado["feedbacks"][0]["data_criacao"] == "2026-11-02T12:00:00"
    assert resultado["feedbacks"][0]["comentario"] == "Sugestão"
    perfil_sql, sql, parametros = consulta.await_args.args
    assert perfil_sql == perfil and parametros == {"usuario_id": 7}
    assert "WHERE usuario_id = :usuario_id" in sql and "ORDER BY data_criacao DESC, id DESC" in sql
    assert "usuario_id" not in listar_meus_feedbacks.args


@pytest.mark.parametrize("falhar", [False, True])
def test_lista_vazia_e_falha_de_consulta_sao_distintas(monkeypatch, falhar):
    monkeypatch.setattr(servico, "executar_consulta", AsyncMock(return_value=[], side_effect=RuntimeError("teste") if falhar else None))
    usuario = UsuarioContexto.model_construct(usuario_id=7, tipo_acesso="gestor")
    resultado = asyncio.run(listar_meus_feedbacks.coroutine(SimpleNamespace(context={"usuario": usuario})))
    assert resultado["status"] == ("ERRO_FERRAMENTA" if falhar else "SEM_RESULTADO")


def test_sem_autenticacao_nao_consulta_banco(monkeypatch):
    consulta = AsyncMock()
    monkeypatch.setattr(servico, "executar_consulta", consulta)
    assert asyncio.run(listar_meus_feedbacks.coroutine(SimpleNamespace(context={})))["status"] == "ACESSO_NEGADO"
    consulta.assert_not_awaited()
