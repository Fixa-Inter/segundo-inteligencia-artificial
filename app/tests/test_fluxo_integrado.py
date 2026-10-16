"""Percorre o grafo compilado com modelos e ferramentas simulados."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from langchain_core.messages import HumanMessage

from app.agents import registro
from app.agents.juiz import AvaliacaoJuiz
from app.graph import fluxo, nos
from app.graph.executor import criar_estado_inicial


def executar_turno():
    grafo = fluxo.construir_grafo()
    estado = criar_estado_inicial(
        [HumanMessage(content="Como acompanho meu chamado?")],
        SimpleNamespace(usuario_id=7, tipo_acesso="solicitante"),
    )
    return asyncio.run(grafo.ainvoke(
        estado, config={"configurable": {"thread_id": "conversa"}}, context={},
    ))


def preparar_fluxo(monkeypatch, avaliacoes):
    monkeypatch.setattr(nos, "proteger_entrada", lambda _: {"bloqueado": False})
    monkeypatch.setattr(nos, "roteador_estruturado", SimpleNamespace(invoke=lambda _: SimpleNamespace(
        intencao="faq", justificativa="Dúvida sobre o aplicativo",
    )))
    especialista = AsyncMock(return_value={
        "resposta_especialista": "Consulte Meus chamados. Contato: teste@exemplo.com",
        "evidencias": ["Trecho consultado"], "erro": None,
    })
    monkeypatch.setattr(fluxo, "executar_faq", especialista)
    julgamento = Mock(side_effect=[AvaliacaoJuiz(veredito=v, feedback="Avaliação") for v in avaliacoes])
    monkeypatch.setattr(registro, "juiz", SimpleNamespace(invoke=julgamento))
    return especialista, julgamento


def test_resposta_aprovada_passou_juiz_e_protecao_saida(monkeypatch):
    especialista, julgamento = preparar_fluxo(monkeypatch, ["aprovado"])
    resultado = executar_turno()
    assert "[EMAIL OMITIDO]" in resultado["resposta_final"]
    assert resultado["veredito"] == "aprovado"
    assert resultado["messages"][-1].content == resultado["resposta_final"]
    especialista.assert_awaited_once()
    assert julgamento.call_count == 1


@pytest.mark.parametrize("segundo_veredito", ["aprovado", "revisar"])
def test_revisao_texto_nao_repete_especialista(monkeypatch, segundo_veredito):
    especialista, julgamento = preparar_fluxo(monkeypatch, ["revisar", segundo_veredito])
    revisao = AsyncMock(return_value={"resposta_especialista": "Texto corrigido", "erro": None})
    monkeypatch.setattr(fluxo, "revisar_resposta", revisao)
    resultado = executar_turno()
    especialista.assert_awaited_once()
    revisao.assert_awaited_once()
    assert julgamento.call_count == 2
    assert resultado["evidencias"] == ["Trecho consultado"]
    if segundo_veredito == "aprovado":
        assert resultado["resposta_final"] == "Texto corrigido"
    else:
        assert resultado["tentativas"] == 2
        assert "Não foi possível validar" in resultado["resposta_final"]


def test_bloqueio_entrada_impede_especialista_e_juiz(monkeypatch):
    especialista, julgamento = preparar_fluxo(monkeypatch, [])
    monkeypatch.setattr(nos, "proteger_entrada", lambda _: {
        "bloqueado": True, "motivo": "teste", "mensagem": "Entrada bloqueada",
    })
    resultado = executar_turno()
    assert resultado["resposta_final"] == "Entrada bloqueada"
    especialista.assert_not_awaited()
    julgamento.assert_not_called()
