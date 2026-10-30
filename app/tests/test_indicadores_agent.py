"""Integração das tools gerenciais e fronteira de roteamento analytics/ajuda."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.agents import indicadores, orquestrador
from app.agents.agentsResult import IndicadoresResultado
from app.agents.prompts.construtor import construir_indicadores_gestor
from app.tools.metricas_kpis import FERRAMENTAS_INDICADORES


def test_agente_indicadores_recebe_36_tools_sem_unidade_editavel(monkeypatch):
    monkeypatch.setattr(indicadores, "create_agent", lambda **kwargs: kwargs)

    agente = indicadores.criar_agente_indicadores(object(), "prompt")
    nomes = [ferramenta.name for ferramenta in agente["tools"]]

    assert set(nomes) == {
        *(ferramenta.name for ferramenta in FERRAMENTAS_INDICADORES),
        "buscar_historico",
    }
    assert len(nomes) == len(set(nomes))
    assert len(FERRAMENTAS_INDICADORES) == 36
    assert "obter_taxa_ocorrencias_alta_prioridade" in nomes
    assert "obter_taxa_recorrencia_local_categoria" in nomes
    assert "obter_taxa_tarefas_concluidas" not in nomes
    assert all(
        "unidade_id" not in ferramenta.tool_call_schema.model_json_schema()["properties"]
        for ferramenta in FERRAMENTAS_INDICADORES
    )


def test_agente_permanece_com_resposta_estruturada(monkeypatch):
    monkeypatch.setattr(indicadores, "create_agent", lambda **kwargs: kwargs)

    agente = indicadores.criar_agente_indicadores(object(), "prompt")

    assert agente["response_format"] is IndicadoresResultado


def test_prompt_indica_tools_fronteiras_e_metricas_nao_disponiveis():
    prompt = construir_indicadores_gestor()

    assert "obter_total_os" in prompt
    assert "obter_solicitacoes_por_unidade" in prompt
    assert "obter_ocorrencias_por_periodo" in prompt
    assert "ajuda_geral" in prompt
    assert "OS-15" in prompt
    assert "não há dados" in prompt
    assert "revisão/aprovação do gestor" in prompt
    assert "ativos no cadastro" not in prompt
    assert "unidade vinculada ao gestor autenticado" in prompt
    assert "não escolhe outra unidade" in prompt
    assert "buscar_historico` apenas para entender o contexto" in prompt
    assert "exigem consulta" in prompt
    assert "INDICADOR_INDISPONIVEL" in prompt
    assert "consulte a tool" in prompt
    assert "não está disponível" in prompt
    assert "não apresente ranking entre unidades" in prompt
    assert "sem prometer tempo real" in prompt
    assert "24 horas" not in prompt
    assert "30 dias" not in prompt


def test_roteador_distingue_contagem_analytics_de_lista_de_registros(monkeypatch):
    async def verificar(mensagem, intencao):
        resposta = orquestrador.DecisaoRoteamento(
            intencao=intencao,
            continua_pendente=False,
            cadastro_em_andamento=False,
            justificativa="Teste de classificação.",
        )
        modelo = SimpleNamespace(ainvoke=AsyncMock(return_value=resposta))
        monkeypatch.setattr(orquestrador, "roteador_estruturado", modelo)

        decisao = await orquestrador.rotear_orquestrador({}, mensagem)
        instrucoes = modelo.ainvoke.await_args.args[0][0].content
        assert "contagens agregadas" in instrucoes
        assert "quais solicitacoes estao pendentes?" in instrucoes
        assert "quantas solicitacoes estao pendentes?" in instrucoes
        return decisao

    contagem = asyncio.run(verificar(
        "Quantas solicitações estão pendentes?", "analytics",
    ))
    lista = asyncio.run(verificar(
        "Quais solicitações estão pendentes?", "ajuda_geral",
    ))

    assert contagem.intencao == "analytics"
    assert lista.intencao == "ajuda_geral"
