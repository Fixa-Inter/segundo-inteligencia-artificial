"""Continuidade de rascunhos pelo orquestrador, sem modelos ou MongoDB reais."""

import asyncio
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

from langchain_core.messages import AIMessage, HumanMessage

from app.agents import orquestrador
from app.graph import continuacoes, nos


def decisao(intencao, *, continua, esclarecer=False, cadastro=None):
    return orquestrador.DecisaoRoteamento(
        intencao=intencao, continua_pendente=continua,
        cadastro_em_andamento=(intencao in {"solicitacao", "ocorrencia"} if cadastro is None else cadastro),
        precisa_esclarecimento=esclarecer, justificativa="Decisão de teste.",
    )


def proposta(*, pausado=False):
    return {
        "id": "rascunho-1", "versao": 1, "status_fluxo": "aguardando_confirmacao",
        "pausado": pausado,
        "dados": {"titulo": "Manutenção no notebook", "descricao_local": "2º andar"},
        "imagens": ["foto"],
    }


def runtime():
    return SimpleNamespace(context={
        "session_id": "sessao", "usuario": SimpleNamespace(usuario_id=7),
    })


def test_orquestrador_recebe_historico_e_rascunhos_ativos_e_pausados(monkeypatch):
    modelo = SimpleNamespace(ainvoke=AsyncMock(
        return_value=decisao("ocorrencia", continua=True)))
    monkeypatch.setattr(orquestrador, "roteador_estruturado", modelo)
    estado = {
        "messages": [
            HumanMessage(content="Registre a manutenção do notebook"),
            AIMessage(content="Em qual sala?"), HumanMessage(content="Sala de aula 3"),
        ],
        "ocorrencia_pendente": proposta(),
        "solicitacao_pendente": proposta(pausado=True),
    }
    resultado = asyncio.run(orquestrador.rotear_orquestrador(estado, "Sala de aula 3"))
    assert resultado.intencao == "ocorrencia"
    entrada = json.loads(modelo.ainvoke.await_args.args[0][1].content)
    assert entrada["historico"][-2]["conteudo"] == "Em qual sala?"
    assert entrada["propostas_ativas"]["ocorrencia"]["dados"]["titulo"] == "Manutenção no notebook"
    assert entrada["propostas_pausadas"]["solicitacao"]["dados"]["descricao_local"] == "2º andar"


def test_detalhe_da_ocorrencia_mantem_rascunho_ativo(monkeypatch):
    roteador = AsyncMock(return_value=decisao("ocorrencia", continua=True))
    atualizar = AsyncMock(return_value=True)
    monkeypatch.setattr(nos, "rotear_orquestrador", roteador)
    monkeypatch.setattr(continuacoes, "atualizar_rascunho_solicitacao", atualizar)
    resultado = asyncio.run(nos.supervisionar({
        "messages": [HumanMessage(content="Manutenção do notebook"),
                     AIMessage(content="Em qual sala?"),
                     HumanMessage(content="Sala de aula 3")],
        "ocorrencia_pendente": proposta(),
    }, runtime()))
    assert resultado["intencao"] == "ocorrencia"
    assert "ocorrencia_pendente" not in resultado
    atualizar.assert_not_awaited()


def test_referencia_a_ocorrencia_pausada_retorna_ao_fluxo(monkeypatch):
    monkeypatch.setattr(nos, "rotear_orquestrador", AsyncMock(
        return_value=decisao("ocorrencia", continua=True)))
    atualizar = AsyncMock(return_value=True)
    monkeypatch.setattr(continuacoes, "atualizar_rascunho_solicitacao", atualizar)
    resultado = asyncio.run(nos.supervisionar({
        "messages": [HumanMessage(content="Quero voltar à ocorrência do notebook")],
        "ocorrencia_pendente": proposta(pausado=True),
    }, runtime()))
    assert resultado["intencao"] == "ocorrencia"
    assert resultado["ocorrencia_pendente"]["pausado"] is False
    assert atualizar.await_args.args[2] == {"pausado": False}


def test_retorno_a_ocorrencia_pausa_solicitacao_ativa(monkeypatch):
    monkeypatch.setattr(nos, "rotear_orquestrador", AsyncMock(
        return_value=decisao("ocorrencia", continua=True)))
    atualizar = AsyncMock(return_value=True)
    monkeypatch.setattr(continuacoes, "atualizar_rascunho_solicitacao", atualizar)
    resultado = asyncio.run(nos.supervisionar({
        "messages": [HumanMessage(content="Voltei à manutenção do notebook")],
        "solicitacao_pendente": proposta(),
        "ocorrencia_pendente": proposta(pausado=True),
    }, runtime()))
    assert resultado["intencao"] == "ocorrencia"
    assert resultado["solicitacao_pendente"]["pausado"] is True
    assert resultado["ocorrencia_pendente"]["pausado"] is False
    assert [chamada.kwargs["tipo"] for chamada in atualizar.await_args_list] == [
        "solicitacao", "ocorrencia",
    ]


def test_novo_registro_do_mesmo_tipo_pausa_o_rascunho_antigo(monkeypatch):
    monkeypatch.setattr(nos, "rotear_orquestrador", AsyncMock(
        return_value=decisao("ocorrencia", continua=False)))
    atualizar = AsyncMock(return_value=True)
    monkeypatch.setattr(continuacoes, "atualizar_rascunho_solicitacao", atualizar)
    resultado = asyncio.run(nos.supervisionar({
        "messages": [HumanMessage(content="Registre outra manutenção")],
        "ocorrencia_pendente": proposta(),
    }, runtime()))
    assert resultado["intencao"] == "ocorrencia"
    assert resultado["ocorrencia_pendente"]["pausado"] is True


def test_decisao_ambigua_nao_altera_propostas(monkeypatch):
    monkeypatch.setattr(nos, "rotear_orquestrador", AsyncMock(
        return_value=decisao("ocorrencia", continua=True, esclarecer=True)))
    atualizar = AsyncMock(return_value=True)
    monkeypatch.setattr(continuacoes, "atualizar_rascunho_solicitacao", atualizar)
    resultado = asyncio.run(nos.supervisionar({
        "messages": [HumanMessage(content="É na sala 3")],
        "solicitacao_pendente": proposta(),
        "ocorrencia_pendente": proposta(),
    }, runtime()))
    assert resultado["esclarecimento_roteamento"]
    atualizar.assert_not_awaited()
