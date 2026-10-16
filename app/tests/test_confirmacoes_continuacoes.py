import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from app.core.confirmacoes import aceite_explicito, classificar_manifestacao
from app.graph import nos
from app.graph import continuacoes


@pytest.mark.parametrize("mensagem", [
    "Sim!", "Confirmo os dados", "Autorizo a alteração", "De acordo.",
    "Pode registrar a solicitação", "Pode anexar as fotos, por favor.", "Sim, pode seguir", "Está correto!",
])
def test_aceites_compartilhados(mensagem):
    assert aceite_explicito(mensagem)


@pytest.mark.parametrize("mensagem", [
    "Pode alterar?", "Sim?", "Como confirmo", "Sim, mas troque o local",
    "Sim, não envie", "Ok, mude o título", "Pode registrar se o local estiver correto",
    "Talvez", "Não", "Confirmo depois", "Sim, o endereço é outro", "Sim, cancelar",
])
def test_perguntas_condicoes_correcoes_nao_autorizam(mensagem):
    assert not aceite_explicito(mensagem)


@pytest.mark.parametrize("mensagem,esperado", [
    ("Cancele a solicitação", "cancelamento"), ("Quero cancelar a ocorrência", "cancelamento"),
    ("Não quero mais continuar", "cancelamento"), ("Não quero continuar", "cancelamento"),
    ("Depois eu continuo", "pausa"), ("Retomar a solicitação", "retomada"),
])
def test_manifestacoes(mensagem, esperado):
    assert classificar_manifestacao(mensagem) == esperado


def proposta(pausado=False):
    return {"id": "proposta", "versao": 1, "status_fluxo": "aguardando_confirmacao", "pausado": pausado}


def contexto():
    return {"session_id": "sessao", "usuario": SimpleNamespace(usuario_id=7)}


def test_sim_continua_proposta_ativa_sem_chamar_modelo(monkeypatch):
    classificar = Mock()
    monkeypatch.setattr(nos, "roteador_estruturado", SimpleNamespace(invoke=classificar))
    resultado = asyncio.run(nos.supervisionar({
        "messages": [HumanMessage(content="Sim")], "solicitacao_pendente": proposta(),
    }, SimpleNamespace(context=contexto())))
    assert resultado["intencao"] == "solicitacao"
    classificar.assert_not_called()


def test_novo_assunto_pausa_rascunho_e_nao_prende_roteamento(monkeypatch):
    salvar = AsyncMock(return_value=True)
    monkeypatch.setattr(continuacoes, "atualizar_rascunho_solicitacao", salvar)
    classificar = Mock(return_value=SimpleNamespace(intencao="faq", justificativa="Novo assunto", continua_pendente=False))
    monkeypatch.setattr(nos, "roteador_estruturado", SimpleNamespace(invoke=classificar))
    resultado = asyncio.run(nos.supervisionar({
        "messages": [HumanMessage(content="O ventilador está quebrado"),
                     AIMessage(content="Em qual sala?"), HumanMessage(content="Como altero minha senha?")],
        "solicitacao_pendente": proposta(),
    }, SimpleNamespace(context=contexto())))
    assert resultado["intencao"] == "faq"
    assert resultado["solicitacao_pendente"]["pausado"] is True
    assert salvar.await_args.args[2] == {"pausado": True}
    assert "ventilador" in classificar.call_args.args[0][1].content


def test_detalhe_continua_coleta_sem_rascunho(monkeypatch):
    classificar = Mock(return_value=SimpleNamespace(intencao="solicitacao", justificativa="Resposta ao local", continua_pendente=True))
    monkeypatch.setattr(nos, "roteador_estruturado", SimpleNamespace(invoke=classificar))
    resultado = asyncio.run(nos.supervisionar({"messages": [
        HumanMessage(content="Preciso consertar um ventilador"), AIMessage(content="Em qual sala?"),
        HumanMessage(content="Na sala 2"),
    ]}, SimpleNamespace(context=contexto())))
    assert resultado["intencao"] == "solicitacao"
    assert "ventilador" in classificar.call_args.args[0][1].content


def test_sim_nao_retoma_rascunho_pausado():
    resultado = asyncio.run(continuacoes.tratar_continuacao({"solicitacao_pendente": proposta(True)}, contexto(), "Sim"))
    assert resultado["esclarecimento_roteamento"]
    assert resultado["intencao"] is None


@pytest.mark.parametrize("mensagem,campo,valor", [
    ("Retomar a solicitação", "pausado", False), ("Cancele a solicitação", "status_fluxo", "cancelada"),
    ("Depois eu continuo", "pausado", True),
])
def test_operacoes_pendentes_persistidas(monkeypatch, mensagem, campo, valor):
    salvar = AsyncMock(return_value=True)
    monkeypatch.setattr(continuacoes, "atualizar_rascunho_solicitacao", salvar)
    resultado = asyncio.run(continuacoes.tratar_continuacao({"solicitacao_pendente": proposta()}, contexto(), mensagem))
    assert resultado["solicitacao_pendente"][campo] == valor
    assert salvar.await_args.kwargs["rascunho_id"] == "proposta"


def test_duas_propostas_exigem_esclarecimento_sem_mutacao(monkeypatch):
    salvar = AsyncMock()
    monkeypatch.setattr(continuacoes, "atualizar_rascunho_solicitacao", salvar)
    resultado = asyncio.run(continuacoes.tratar_continuacao({
        "solicitacao_pendente": proposta(), "ocorrencia_pendente": proposta(),
    }, contexto(), "Sim"))
    assert resultado["esclarecimento_roteamento"]
    salvar.assert_not_awaited()


def test_pergunta_edicao_nao_executa_mutacao(monkeypatch):
    from datetime import datetime, timezone
    from app.tools.ajuda_geral import edicoes
    iniciar = AsyncMock(return_value=True)
    monkeypatch.setattr(edicoes, "iniciar_acao", iniciar)
    resultado = asyncio.run(edicoes._executar_pendente(
        {"turno_id": "agora", "mensagem_atual": "Pode alterar?"},
        SimpleNamespace(usuario_id=7), "sessao",
        {"status": "aguardando_confirmacao", "turno_id": "antes", "criada_em": datetime.now(timezone.utc)},
    ))
    assert resultado["status"] == "CONFIRMACAO_NECESSARIA"
    iniciar.assert_not_awaited()


def test_imagem_sem_texto_continua_apos_validacao(monkeypatch):
    monkeypatch.setattr(nos, "proteger_entrada", lambda _: {"bloqueado": False})
    estado = {"messages": [HumanMessage(content="")], "perfil": "tecnico", "imagens_recebidas": True,
              "ocorrencia_pendente": {**proposta(), "status_fluxo": "aguardando_imagem"}}
    assert nos.validar_entrada(estado)["entrada_valida"]
    resultado = asyncio.run(nos.supervisionar(estado, SimpleNamespace(context=contexto())))
    assert resultado["intencao"] == "ocorrencia"
