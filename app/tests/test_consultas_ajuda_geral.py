"""Distribuição de consultas e cadastros entre os agentes."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from langchain_core.messages import HumanMessage

from app.agents import ajuda_geral, orquestrador, solicitacoes
from app.graph import continuacoes, nos


CONSULTAS = {
    "listar_minhas_solicitacoes",
    "listar_minhas_ocorrencias",
    "listar_minhas_ordens_servico",
    "buscar_ordem_servico",
    "listar_todas_solicitacoes_pendentes",
    "listar_todas_ordens_servico",
    "buscar_tecnicos_disponiveis",
}
CADASTROS = {
    "salvar_rascunho_solicitacao",
    "criar_solicitacao",
    "salvar_rascunho_ocorrencia",
    "criar_ocorrencia",
}


@pytest.mark.parametrize("perfil, consultas_esperadas", [
    ("solicitante", {"listar_minhas_solicitacoes"}),
    ("tecnico", {
        "listar_minhas_solicitacoes", "listar_minhas_ocorrencias",
        "listar_minhas_ordens_servico", "buscar_ordem_servico",
    }),
    ("administrador", {
        "listar_minhas_solicitacoes", "listar_minhas_ocorrencias",
        "listar_minhas_ordens_servico", "buscar_ordem_servico",
    }),
    ("gestor", {
        "listar_minhas_ocorrencias", "listar_minhas_ordens_servico",
        "buscar_ordem_servico", "listar_todas_solicitacoes_pendentes",
        "listar_todas_ordens_servico", "buscar_tecnicos_disponiveis",
    }),
])
def test_consultas_ficam_no_ajuda_geral_e_respeitam_perfil(
    monkeypatch, perfil, consultas_esperadas,
):
    monkeypatch.setattr(ajuda_geral, "create_agent", lambda **kwargs: kwargs)

    agente = ajuda_geral.criar_agente_ajuda_geral(None, "instrução", perfil=perfil)
    nomes = [ferramenta.name for ferramenta in agente["tools"]]

    assert len(nomes) == len(set(nomes))
    assert set(nomes) & CONSULTAS == consultas_esperadas
    assert set(nomes).isdisjoint(CADASTROS)
    assert "buscar_historico" in nomes


@pytest.mark.parametrize("perfil, cadastros_esperados", [
    ("solicitante", {"salvar_rascunho_solicitacao", "criar_solicitacao"}),
    ("tecnico", CADASTROS),
    ("administrador", CADASTROS),
    ("gestor", {"salvar_rascunho_ocorrencia", "criar_ocorrencia"}),
])
def test_agente_de_cadastro_preserva_criacao_sem_consultas(
    monkeypatch, perfil, cadastros_esperados,
):
    monkeypatch.setattr(solicitacoes, "create_agent", lambda **kwargs: kwargs)

    agente = solicitacoes.criar_agente_solicitacoes(
        None, "instrução", **{"tecnico" if perfil == "administrador" else perfil: True},
    )
    nomes = [ferramenta.name for ferramenta in agente["tools"]]

    assert len(nomes) == len(set(nomes))
    assert set(nomes).isdisjoint(CONSULTAS)
    assert set(nomes) & CADASTROS == cadastros_esperados
    assert "buscar_historico" in nomes


@pytest.mark.parametrize("cadastro, continua, intencao_esperada", [
    (False, False, "ajuda_geral"),
    (True, False, "ocorrencia"),
    (False, True, "ocorrencia"),
])
def test_roteador_separa_consulta_de_cadastro_e_continuacao(
    monkeypatch, cadastro, continua, intencao_esperada,
):
    resposta = orquestrador.DecisaoRoteamento(
        intencao="ocorrencia",
        continua_pendente=continua,
        cadastro_em_andamento=cadastro,
        justificativa="Decisão de teste.",
    )
    modelo = AsyncMock()
    modelo.ainvoke.return_value = resposta
    monkeypatch.setattr(orquestrador, "roteador_estruturado", modelo)

    decisao = asyncio.run(orquestrador.rotear_orquestrador({}, "Minhas ocorrências"))

    assert decisao.intencao == intencao_esperada


def test_consulta_pausa_rascunho_e_segue_para_ajuda_geral(monkeypatch):
    resposta = orquestrador.DecisaoRoteamento(
        intencao="ocorrencia", continua_pendente=False,
        cadastro_em_andamento=False, justificativa="Listar registros existentes.",
    )
    modelo = AsyncMock()
    modelo.ainvoke.return_value = resposta
    monkeypatch.setattr(orquestrador, "roteador_estruturado", modelo)
    atualizar = AsyncMock(return_value=True)
    monkeypatch.setattr(continuacoes, "atualizar_rascunho_solicitacao", atualizar)
    estado = {
        "messages": [HumanMessage(content="Quero ver minhas ocorrências")],
        "ocorrencia_pendente": {
            "id": "rascunho-1", "versao": 1,
            "status_fluxo": "aguardando_confirmacao", "pausado": False,
            "dados": {"titulo": "Manutenção do notebook"},
        },
    }
    runtime = SimpleNamespace(context={
        "session_id": "sessao", "usuario": SimpleNamespace(usuario_id=7),
    })

    resultado = asyncio.run(nos.supervisionar(estado, runtime))

    assert resultado["intencao"] == "ajuda_geral"
    assert resultado["ocorrencia_pendente"]["pausado"] is True
    atualizar.assert_awaited_once()
