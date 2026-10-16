import asyncio
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import httpx
import pytest
from langchain_core.messages import HumanMessage
from pydantic import ValidationError

from app.agents.juiz import AvaliacaoJuiz, RespostaRevisada, julgar_resposta, revisar_resposta
from app.graph.transicoes import decidir_apos_julgamento
from app.services.solicitacoes import criarSolicitacao as servico
from app.tools.toolsRequest import CriarSolicitacaoEntrada


def dados():
    return dict(categoria_equipamento_id=2, local_endereco_id=6,
                titulo="Notebook com defeito", descricao_problema="Notebook pegando fogo",
                descricao_local="Perto do ar condicionado")


def cliente_simulado(monkeypatch, status, corpo):
    resposta = httpx.Response(status, json=corpo,
                              request=httpx.Request("POST", "https://example.com"))
    post = AsyncMock(return_value=resposta)
    cliente = SimpleNamespace(post=post)
    contexto = AsyncMock()
    contexto.__aenter__.return_value = cliente
    monkeypatch.setattr(servico.httpx, "AsyncClient", Mock(return_value=contexto))
    monkeypatch.setattr(servico, "FIXA_URL_BASE_API", "https://example.com")
    return post


def test_payload_segue_swagger_e_interpreta_sucesso(monkeypatch):
    post = cliente_simulado(monkeypatch, 200, {"id": 15, "titulo": "Notebook", "status": "PENDENTE"})
    resultado = asyncio.run(servico.adicionar_solicitacao(
        CriarSolicitacaoEntrada(**dados()), "token-teste", imagens=["https://example.com/foto.jpg"]))
    spec = json.loads((Path(__file__).resolve().parents[2] / "docs/api/swagger.json").read_text(encoding="utf-8"))
    contrato = spec["components"]["schemas"]["ProblemaCriarInputDTO"]
    conteudo = post.call_args.kwargs["json"]
    assert set(conteudo) == set(contrato["required"])
    assert conteudo["localUnidadeID"] == 6
    assert conteudo["categoriaEquipamentoId"] == 2
    assert conteudo["descricaoProblema"] == dados()["descricao_problema"]
    assert conteudo["descricaoLocal"] == dados()["descricao_local"]
    assert conteudo["urlsFoto"] == ["https://example.com/foto.jpg"]
    assert post.call_args.kwargs["headers"]["Authorization"] == "Bearer token-teste"
    assert resultado["status"] == "SUCESSO"
    assert resultado["problema_id"] == 15
    post.assert_awaited_once()


@pytest.mark.parametrize("descricao", [None, "", "   "])
def test_descricao_local_obrigatoria(descricao):
    with pytest.raises(ValidationError):
        CriarSolicitacaoEntrada(**{**dados(), "descricao_local": descricao})


def test_recusa_preserva_detalhe_sem_repetir_post(monkeypatch):
    post = cliente_simulado(monkeypatch, 400, {"message": "Local inválido", "token": "token-teste"})
    resultado = asyncio.run(servico.adicionar_solicitacao(
        CriarSolicitacaoEntrada(**dados()), "token-teste", imagens=["https://example.com/foto.jpg"]))
    assert resultado["status"] == "ERRO_API"
    assert resultado["http_status"] == 400
    assert "Local inválido" in resultado["detalhes_api"]
    assert "token-teste" not in resultado["detalhes_api"]
    post.assert_awaited_once()


def test_juiz_recebe_relato_anterior_e_confirmacao(monkeypatch):
    juiz = Mock()
    juiz.invoke.return_value = AvaliacaoJuiz(veredito="aprovado", feedback="OK")
    monkeypatch.setitem(sys.modules, "app.agents.registro", SimpleNamespace(juiz=juiz))
    estado = {"perfil": "solicitante", "messages": [
        HumanMessage(content="Um notebook está pegando fogo"),
        HumanMessage(content="Pode registrar a solicitação"),
    ], "resposta_especialista": "A API recusou o cadastro", "evidencias": []}
    assert julgar_resposta(estado)["veredito"] == "aprovado"
    entrada = juiz.invoke.call_args.args[0][-1].content
    assert "notebook está pegando fogo" in entrada
    assert "Pode registrar a solicitação" in entrada


def test_revisao_somente_texto_limitada_a_uma_tentativa(monkeypatch):
    modelo = Mock()
    modelo.with_structured_output.return_value.ainvoke = AsyncMock(
        return_value=RespostaRevisada(resposta="A API recusou o cadastro."))
    monkeypatch.setitem(sys.modules, "app.agents.modelos", SimpleNamespace(llm_especialista=modelo))
    estado = {"veredito": "revisar", "tentativas": 1, "perfil": "solicitante",
              "evidencias": ['{"status":"ERRO_API"}'], "feedback_juiz": "Corrigir o texto"}
    assert decidir_apos_julgamento(estado) == "revisar_resposta"
    revisado = asyncio.run(revisar_resposta(estado))
    assert revisado["resposta_especialista"] == "A API recusou o cadastro."
    modelo.bind_tools.assert_not_called()
    assert "evidencias" not in revisado
    assert decidir_apos_julgamento({**estado, "tentativas": 2}) == "fallback"
    assert decidir_apos_julgamento({**estado, "veredito": "aprovado"}) == "proteger_saida"
