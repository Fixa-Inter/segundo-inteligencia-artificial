"""Reproduções isoladas das divergências, sem API, modelos ou bancos reais."""

import asyncio
from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from langchain_core.messages import HumanMessage, SystemMessage

from app.graph import nos, fluxo
from app.graph.executor import criar_estado_inicial
from app.guardrails.validacao import anonimizar_entrada, remover_dados_pessoais_saida
from app.tools.ajuda_geral.edicoes import _confirmacao_edicao


def test_novo_turno_fora_escopo_nao_herda_bloqueio_juiz(monkeypatch):
    monkeypatch.setattr(nos, "proteger_entrada", lambda _: {"bloqueado": False})
    decisoes = iter(["faq", "fora_de_escopo"])
    async def rotear(*_):
        return SimpleNamespace(intencao=next(decisoes), justificativa="Teste",
                               continua_pendente=False, precisa_esclarecimento=False)
    monkeypatch.setattr(nos, "rotear_orquestrador", rotear)
    monkeypatch.setattr(fluxo, "executar_faq", AsyncMock(return_value={
        "resposta_especialista": "Resposta candidata", "erro": None,
    }))
    monkeypatch.setattr(fluxo, "julgar_resposta", lambda _: {
        "veredito": "bloqueado", "feedback_juiz": "Sem evidência", "tentativas": 0,
    })
    grafo = fluxo.construir_grafo()
    configuracao = {"configurable": {"thread_id": "auditoria"}}
    usuario = SimpleNamespace(usuario_id=1, tipo_acesso="solicitante")

    async def executar():
        for pergunta in ["Como uso o aplicativo?", "Fale sobre futebol"]:
            resultado = await grafo.ainvoke(
                criar_estado_inicial([HumanMessage(content=pergunta)], usuario),
                config=configuracao, context={},
            )
        return resultado

    resultado = asyncio.run(executar())
    assert resultado["intencao"] == "fora_de_escopo"
    assert "Posso ajudar" in resultado["resposta_final"]


def test_confirmacao_solicitacao_disponibiliza_contexto_roteador(monkeypatch):
    entradas = []

    async def classificar(estado, pergunta):
        entradas.extend(estado["messages"])
        return SimpleNamespace(intencao="solicitacao", justificativa="Teste",
                               continua_pendente=False, precisa_esclarecimento=False)

    monkeypatch.setattr(nos, "rotear_orquestrador", classificar)
    resultado = asyncio.run(nos.supervisionar({
        "messages": [HumanMessage(content="Cadastre o ventilador quebrado"),
                     HumanMessage(content="Sim")],
        "solicitacao_pendente": {"status_fluxo": "aguardando_confirmacao"},
    }, SimpleNamespace(context={})))
    assert resultado["intencao"] == "solicitacao"



def test_cnpj_sem_pontuacao_anonimizado_inteiro():
    texto, mapa = anonimizar_entrada("CNPJ 12345678000190")
    assert list(mapa.values()) == ["12345678000190"]
    assert texto.startswith("CNPJ [PII_CNPJ_") and texto.endswith("]")


def test_pergunta_nao_autoriza_edicao():
    assert _confirmacao_edicao("Pode alterar?") is False


def test_cadastro_exige_confirmacao_posterior_proposta(monkeypatch):
    from app.tools.ocorrencias import criarOcorrencia as ferramenta

    contexto = {"mensagem_atual": "Pode registrar", "turno_id": "turno-atual"}
    usuario = SimpleNamespace(tipo_acesso="tecnico", usuario_id=1, access_token="teste")
    monkeypatch.setattr(ferramenta, "_contexto", lambda _: (contexto, usuario, "sessao"))
    monkeypatch.setattr(ferramenta, "obter_rascunho_solicitacao", AsyncMock(return_value={
        "turno_id": "turno-atual", "status_fluxo": "aguardando_confirmacao",
        "imagens": ["https://exemplo.com/foto.jpg"], "dados": {
            "local_endereco_id": 1, "categoria_equipamento_id": 2,
            "categoria_problema_id": "INFORMATICA", "prioridade": "ALTA",
            "titulo": "Computador", "descricao_ocorrencia": "Troca realizada",
            "descricao_local": "Sala principal",
        },
    }))
    monkeypatch.setattr(ferramenta, "obter_unidade_id", AsyncMock(return_value=1))
    monkeypatch.setattr(ferramenta, "validar_selecao", AsyncMock())
    monkeypatch.setattr(ferramenta, "atualizar_rascunho_solicitacao", AsyncMock(return_value=True))

    @asynccontextmanager
    async def cliente_simulado():
        yield object()

    monkeypatch.setattr(ferramenta, "abrir_cliente_qdrant", cliente_simulado)
    cadastrar = AsyncMock(return_value={"status": "SUCESSO", "ocorrencia_id": 3})
    monkeypatch.setattr(ferramenta, "adicionar_ocorrencia", cadastrar)
    resultado = asyncio.run(ferramenta.criar_ocorrencia.coroutine(None))
    assert resultado["status"] == "CONFIRMACAO_NECESSARIA"
    cadastrar.assert_not_awaited()


def test_saida_remove_dados_pessoais_sem_reescrever_texto():
    assert remover_dados_pessoais_saida("Contato: teste@exemplo.com") == "Contato: [EMAIL OMITIDO]"


def test_instrucao_utiliza_data_atual_construcao(monkeypatch):
    from datetime import datetime, timezone
    from importlib import import_module
    from app.agents.prompts.reutilizaveis import construir_contexto_temporal

    modulo = import_module("app.core.tempo")
    relogio = SimpleNamespace(now=lambda *_: datetime(2099, 1, 2, 12, tzinfo=timezone.utc))
    monkeypatch.setattr(modulo, "datetime", relogio)
    assert "2099" in construir_contexto_temporal()


@pytest.mark.xfail(strict=True, reason="D07: indicador gerencial não recebe consulta operacional")
def test_indicadores_recebe_ferramenta_dados_operacionais(monkeypatch):
    from app.agents import indicadores

    monkeypatch.setattr(indicadores, "create_agent", lambda **argumentos: argumentos)
    argumentos = indicadores.criar_agente_indicadores(object(), "Instrução")
    assert any(ferramenta.name != "buscar_historico" for ferramenta in argumentos["tools"])
