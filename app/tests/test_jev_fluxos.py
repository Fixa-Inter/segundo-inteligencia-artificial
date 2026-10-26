"""Contratos das duas decisões do JEV, sem chamadas externas."""

import asyncio
import json
from importlib import import_module
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from app.graph import nos
from app.services.gerais import rotear
from app.services.gerais.jev import DecisaoIncertaJEV, ErroJEV, ler_choice, ler_noul

juiz = import_module("app.agents.juiz")


def respostas_roteador(intencao="solicitacao", confianca=0.9, continua=0.1):
    return {"model": "jev-teste", "answers": {
        "intencao": {"type": "choice", "choice": intencao, "confidence": confianca},
        "continua_pendente": {"type": "noul", "noul": continua},
    }}


def respostas_juiz(veredito="aprovado", motivo="nenhum", sem_suporte=0.05,
                  corrigivel=0.05, risco=0.05, confianca=0.9):
    return {"model": "jev-teste", "answers": {
        "veredito": {"type": "choice", "choice": veredito, "confidence": confianca},
        "motivo": {"type": "choice", "choice": motivo, "confidence": 0.9},
        "afirmacao_sem_suporte": {"type": "noul", "noul": sem_suporte},
        "correcao_textual": {"type": "noul", "noul": corrigivel},
        "risco_grave": {"type": "noul", "noul": risco},
    }}


def estado_juiz(evidencias=None):
    return {
        "perfil": "solicitante",
        "messages": [HumanMessage(content="O ventilador queimou"),
                     HumanMessage(content="A solicitação foi criada?")],
        "resposta_especialista": "A solicitação foi criada.",
        "evidencias": evidencias or [],
        "tentativas": 0,
    }


def test_roteamento_usa_historico_e_proposta_serializavel(monkeypatch):
    consultar = AsyncMock(return_value=respostas_roteador(continua=0.97))
    monkeypatch.setattr(rotear, "consultar_jev", consultar)
    estado = {
        "messages": [HumanMessage(content="Preciso consertar ventilador"),
                     AIMessage(content="Em qual sala?"), HumanMessage(content="Sala 2")],
        "solicitacao_pendente": {"status_fluxo": "aguardando_confirmacao",
                                  "dados": {"titulo": "Ventilador"}},
    }
    decisao = asyncio.run(rotear.rotear_jev(estado, "Sala 2"))
    assert decisao["intencao"] == "solicitacao"
    assert decisao["continua_pendente"]
    corpo = consultar.await_args.args[0]
    assert corpo["historico"][0]["conteudo"] == "Preciso consertar ventilador"
    assert corpo["propostas_ativas"]["solicitacao"]["dados"]["titulo"] == "Ventilador"
    json.dumps(corpo, allow_nan=False)


def test_roteamento_incerto_pede_esclarecimento_sem_pausar_proposta(monkeypatch):
    monkeypatch.setattr(rotear, "consultar_jev", AsyncMock(return_value=respostas_roteador(
        intencao="faq", confianca=0.2, continua=0.5)))
    estado = {"messages": [HumanMessage(content="E isso?")],
              "solicitacao_pendente": {"status_fluxo": "aguardando_confirmacao"}}
    with pytest.raises(DecisaoIncertaJEV):
        asyncio.run(rotear.rotear_jev(estado, "E isso?"))
    monkeypatch.setattr(nos, "rotear_orquestrador", AsyncMock(return_value=SimpleNamespace(
        intencao="faq", justificativa="Decisão incerta", continua_pendente=False,
        precisa_esclarecimento=True,
    )))
    resultado = asyncio.run(nos.supervisionar(estado, SimpleNamespace(context={})))
    assert resultado["esclarecimento_roteamento"]
    assert "solicitacao_pendente" not in resultado


@pytest.mark.parametrize("evidencias,corrigivel,esperado", [
    ([], 0.95, "bloqueado"),
    ([json.dumps({"ferramenta": "criar_solicitacao", "status_execucao": "success",
                  "status_operacao": "ERRO_API"})], 0.95, "revisar"),
])
def test_juiz_distingue_falta_de_evidencia_de_falha_corrigivel(
    monkeypatch, evidencias, corrigivel, esperado,
):
    consultar = AsyncMock(return_value=respostas_juiz(
        veredito="bloqueado", motivo="contradicao_evidencia",
        sem_suporte=0.95, corrigivel=corrigivel))
    monkeypatch.setattr(juiz, "consultar_jev", consultar)
    resultado = asyncio.run(juiz.julgar_resposta(estado_juiz(evidencias)))
    assert resultado["veredito"] == esperado
    assert resultado["tentativas"] == (1 if esperado == "revisar" else 0)
    assert resultado["feedback_juiz"]
    json.dumps(consultar.await_args.args[0], allow_nan=False)


def test_juiz_bloqueia_risco_grave_mesmo_se_choice_aprova(monkeypatch):
    monkeypatch.setattr(juiz, "consultar_jev", AsyncMock(return_value=respostas_juiz(
        risco=0.95)))
    assert asyncio.run(juiz.julgar_resposta(estado_juiz()))["veredito"] == "bloqueado"


def test_motivo_inconsistente_com_baixa_confianca_nao_bloqueia(monkeypatch):
    resposta = respostas_juiz(motivo="clareza")
    resposta["answers"]["motivo"]["confidence"] = 0.4
    monkeypatch.setattr(juiz, "consultar_jev", AsyncMock(return_value=resposta))

    resultado = asyncio.run(juiz.julgar_resposta(estado_juiz()))
    assert resultado["veredito"] == "aprovado"


def test_motivo_de_permissao_nao_e_ignorado_por_baixa_confianca(monkeypatch):
    resposta = respostas_juiz(motivo="permissao")
    resposta["answers"]["motivo"]["confidence"] = 0.4
    monkeypatch.setattr(juiz, "consultar_jev", AsyncMock(return_value=resposta))

    resultado = asyncio.run(juiz.julgar_resposta(estado_juiz()))
    assert resultado["veredito"] == "bloqueado"


def test_juiz_reavalia_uma_vez_bloqueio_sem_motivo(monkeypatch):
    consultar = AsyncMock(side_effect=[
        respostas_juiz(veredito="bloqueado", motivo="nenhum"),
        respostas_juiz(veredito="aprovado", motivo="nenhum"),
    ])
    monkeypatch.setattr(juiz, "consultar_jev", consultar)
    estado = estado_juiz()
    estado["messages"] = [
        HumanMessage(content="Consertei o notebook que pegou fogo"),
        HumanMessage(content="Apenas apaguei o fogo e levei o notebook ao Helpdesk"),
    ]
    estado["resposta_especialista"] = "Vou registrar apenas o combate ao fogo e o transporte."

    resultado = asyncio.run(juiz.julgar_resposta(estado))
    assert resultado["veredito"] == "aprovado"
    assert consultar.await_count == 2
    assert "Helpdesk" in str(consultar.await_args_list[0].args[0]["historico"])
    assert "avaliacao_anterior" not in consultar.await_args_list[0].args[0]
    assert consultar.await_args_list[1].args[0]["avaliacao_anterior"]["motivo"] == "nenhum"


def test_juiz_mantem_bloqueio_se_reavaliacao_continua_sem_motivo(monkeypatch):
    consultar = AsyncMock(return_value=respostas_juiz(veredito="bloqueado", motivo="nenhum"))
    monkeypatch.setattr(juiz, "consultar_jev", consultar)
    resultado = asyncio.run(juiz.julgar_resposta(estado_juiz()))
    assert resultado["veredito"] == "bloqueado"
    assert "inconclusivo" in resultado["feedback_juiz"]
    assert consultar.await_count == 2


def test_juiz_nao_reavalia_risco_grave_sem_motivo(monkeypatch):
    consultar = AsyncMock(return_value=respostas_juiz(
        veredito="bloqueado", motivo="nenhum", risco=0.95))
    monkeypatch.setattr(juiz, "consultar_jev", consultar)
    resultado = asyncio.run(juiz.julgar_resposta(estado_juiz()))
    assert resultado["veredito"] == "bloqueado"
    consultar.assert_awaited_once()


def test_juiz_bloqueia_falha_de_transporte(monkeypatch):
    monkeypatch.setattr(juiz, "consultar_jev", AsyncMock(side_effect=ErroJEV("sem conexão")))
    resultado = asyncio.run(juiz.julgar_resposta(estado_juiz()))
    assert resultado["veredito"] == "bloqueado"
    assert resultado["erro"]


def test_respostas_invalidas_sao_rejeitadas():
    with pytest.raises(ErroJEV):
        ler_choice({"x": {"type": "choice", "choice": "faq", "confidence": float("nan")}},
                   "x", {"faq"})
    with pytest.raises(ErroJEV):
        ler_noul({"x": {"type": "noul", "noul": 1.2}}, "x")


def test_endpoint_classificacao_preserva_contrato(monkeypatch):
    from app.api.routes.classificacao_problema import classificar_problema
    from app.schemas.ClassificarProblema import ClassificarProblemaRequest

    julgar = import_module("app.services.gerais.julgar")
    monkeypatch.setattr(julgar, "consultar_jev", AsyncMock(return_value={"answers": {
        "veredito": {"type": "choice", "choice": "CLIMATIZACAO", "confidence": 0.9},
        "CLIMATIZACAO": {"type": "noul", "noul": 0.95},
    }}))
    resultado = asyncio.run(classificar_problema(ClassificarProblemaRequest(
        titulo="Ventilador", descricao="Não ventila", categoria_equipamento="Ventilador",
    )))
    assert resultado.problema_classificado is True
    assert resultado.classificacao == "CLIMATIZACAO"
