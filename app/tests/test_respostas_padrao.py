"""Limitações conhecidas recebem texto fixo sem mascarar falhas operacionais."""

import asyncio
import json
from importlib import import_module
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from langchain_core.messages import HumanMessage

from app.agents.agentsResult import FAQResultado, SolicitacaoOcorrenciaResultado
from app.core.respostas import FERRAMENTA_INDISPONIVEL, FAQ_SEM_INFORMACAO, TRECHO_FAQ_AUSENTE
from app.graph.respostas_padrao import preparar_resposta_padrao, resposta_padrao_validada
from app.graph import fluxo, nos
from app.graph.executor import criar_estado_inicial
from app.schemas import UsuarioContexto


def evidencia(ferramenta="buscar_faq", resultado=TRECHO_FAQ_AUSENTE, status_execucao="success", status_operacao=None):
    return json.dumps({"ferramenta": ferramenta, "resultado": resultado,
                       "status_execucao": status_execucao, "status_operacao": status_operacao})


@pytest.mark.parametrize("intencao,status,retorno,texto", [
    ("faq", "SEM_RESULTADO", "Trechos recuperados sobre outro assunto", FAQ_SEM_INFORMACAO),
    ("faq", "SUCESSO", TRECHO_FAQ_AUSENTE, FAQ_SEM_INFORMACAO),
    ("ajuda_geral", "FERRAMENTA_INDISPONIVEL", None, FERRAMENTA_INDISPONIVEL),
    ("solicitacao", "FERRAMENTA_INDISPONIVEL", None, FERRAMENTA_INDISPONIVEL),
])
def test_grafo_entrega_texto_padrao_sem_cadastro_ou_feedback_automatico(monkeypatch, intencao, status, retorno, texto):
    juiz = import_module("app.agents.juiz")
    usuario = UsuarioContexto.model_construct(usuario_id=7, tipo_acesso="tecnico", access_token="teste")
    evidencias = [evidencia(resultado=retorno)] if intencao == "faq" else []
    formato = SolicitacaoOcorrenciaResultado if intencao == "solicitacao" else FAQResultado
    resposta = formato(agente=intencao, status=status, resposta="Resposta genérica que deve ser substituída")
    monkeypatch.setattr(nos, "executar_com_evidencias", AsyncMock(return_value=({"structured_response": resposta}, evidencias)))
    monkeypatch.setattr(nos, "obter_rascunho_solicitacao", AsyncMock(return_value=None))
    julgar = AsyncMock(side_effect=AssertionError("O texto fixo já foi validado pelo backend"))
    executar = AsyncMock()
    monkeypatch.setattr(juiz, "consultar_jev", julgar)
    monkeypatch.setattr(fluxo, "executar_operacoes", executar)
    monkeypatch.setattr(fluxo, "validar_entrada", lambda estado: {"entrada_valida": True})
    monkeypatch.setattr(fluxo, "supervisionar", lambda estado: {"intencao": intencao})
    monkeypatch.setattr(fluxo, "classificar_emocao", AsyncMock(return_value={"emocao": "NEUTRO"}))
    grafo = fluxo.construir_grafo()
    estado = criar_estado_inicial([HumanMessage(content="Quero saber como cadastrar um evento")], usuario)
    resultado = asyncio.run(grafo.ainvoke(
        estado, config={"configurable": {"thread_id": "teste"}},
        context={"usuario": usuario, "session_id": "sessao", "turno_id": "turno", "imagens": [],
                 "mensagem_atual": "Quero saber como cadastrar um evento", "operacoes_pendentes": []},
    ))
    assert resultado["resposta_final"] == texto
    assert resultado["veredito"] == "aprovado"
    assert resultado["erro"] is None
    assert not resultado["operacoes_pendentes"] and not resultado["resultados_operacoes"]
    assert not resultado["propostas_apresentadas"]
    julgar.assert_not_awaited()
    executar.assert_not_awaited()


@pytest.mark.parametrize("evidencias,contexto", [
    ([evidencia(status_execucao="error")], {}),
    ([evidencia(status_operacao="ERRO_FERRAMENTA")], {}),
    ([evidencia(status_operacao="TIMEOUT")], {}),
    ([evidencia(status_operacao="ACESSO_NEGADO")], {}),
    ([evidencia(resultado={"http_status": 401})], {}),
    ([evidencia(status_operacao="RESULTADO_INDETERMINADO")], {}),
    ([evidencia(ferramenta="criar_evento", status_operacao="SUCESSO")], {}),
    ([evidencia(ferramenta="salvar_rascunho_evento", status_operacao="RASCUNHO_SALVO")], {}),
    ([evidencia(ferramenta="anexar_foto_solicitacao")], {}),
    ([evidencia()], {"operacoes_pendentes": [{"tipo": "evento"}]}),
    ([evidencia()], {"resultados_operacoes": [{"tipo": "evento", "resultado": {"status": "SUCESSO"}}]}),
])
@pytest.mark.parametrize("status,intencao", [("SEM_RESULTADO", "faq"), ("FERRAMENTA_INDISPONIVEL", "ajuda_geral")])
def test_falhas_permissoes_e_escritas_nao_sao_substituidas(evidencias, contexto, status, intencao):
    assert preparar_resposta_padrao(status, intencao, evidencias, contexto) == {}


@pytest.mark.parametrize("status,intencao,evidencias", [
    ("SEM_RESULTADO", "faq", []),
    ("SEM_RESULTADO", "ajuda_geral", [evidencia(resultado={"status": "SEM_RESULTADO"})]),
    ("SUCESSO", "faq", [evidencia(resultado="Informação suficiente para responder")]),
    ("AGUARDANDO_INFORMACAO", "faq", []),
    ("ERRO_FERRAMENTA", "faq", [evidencia()]),
])
def test_nao_padroniza_sem_causa_identificada(status, intencao, evidencias):
    assert preparar_resposta_padrao(status, intencao, evidencias, {}) == {}


def test_marcador_nao_aprova_texto_livre_nem_erro():
    estado = {"intencao": "ajuda_geral", "motivo_resposta_padrao": "ferramenta_indisponivel",
              "resposta_especialista": "O evento foi cadastrado", "evidencias": []}
    assert resposta_padrao_validada(estado) is None
    estado.update(resposta_especialista=FERRAMENTA_INDISPONIVEL, erro="Falha de conexão")
    assert resposta_padrao_validada(estado) is None


def test_fallback_tecnico_continua_diferente_de_funcionalidade_ausente():
    resultado = nos.tratar_erro({"intencao": "faq", "erro": "Conexão recusada", "veredito": "bloqueado"})
    assert resultado["resposta_final"] not in {FERRAMENTA_INDISPONIVEL, FAQ_SEM_INFORMACAO}
