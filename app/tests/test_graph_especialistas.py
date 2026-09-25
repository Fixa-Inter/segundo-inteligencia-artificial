import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from langchain_core.messages import HumanMessage

from app.agents.agentsResult import (
    AnalyticsResultado,
    FeedbackResultado,
    VisualizacaoResultado,
)
from app.graph import nodes


def criar_runtime():
    return SimpleNamespace(
        context={
            "usuario": SimpleNamespace(usuario_id=10),
            "imagens": [],
        }
    )


def criar_estado(perfil: str = "gestor") -> dict:
    return {
        "messages": [HumanMessage(content="Mensagem de teste")],
        "perfil": perfil,
    }


def test_executar_analytics_gestor(monkeypatch) -> None:
    resposta = AnalyticsResultado(
        agente="analytics",
        resposta="Foram encontrados 10 chamados.",
        status="SUCESSO",
    )
    agente = SimpleNamespace(
        ainvoke=AsyncMock(
            return_value={"structured_response": resposta}
        )
    )
    monkeypatch.setattr(nodes, "analytics_gestor", agente)

    resultado = asyncio.run(
        nodes.executar_analytics(
            criar_estado(),
            criar_runtime(),
        )
    )

    assert resultado == {
        "resposta_especialista": resposta.resposta,
        "erro": None,
    }
    agente.ainvoke.assert_awaited_once()


def test_analytics_bloqueia_perfil_sem_permissao(
    monkeypatch,
) -> None:
    agente = SimpleNamespace(ainvoke=AsyncMock())
    monkeypatch.setattr(nodes, "analytics_gestor", agente)

    resultado = asyncio.run(
        nodes.executar_analytics(
            criar_estado("solicitante"),
            criar_runtime(),
        )
    )

    assert resultado["erro"] is None
    assert "permissao" in resultado["resposta_especialista"]
    agente.ainvoke.assert_not_awaited()


def test_executar_visualizacao_gestor(monkeypatch) -> None:
    resposta = VisualizacaoResultado(
        agente="visualizacao",
        resposta="Use um grafico de barras.",
        status="SUCESSO",
    )
    agente = SimpleNamespace(
        ainvoke=AsyncMock(
            return_value={"structured_response": resposta}
        )
    )
    monkeypatch.setattr(nodes, "visualizacoes_gestor", agente)

    resultado = asyncio.run(
        nodes.executar_visualizacao(
            criar_estado(),
            criar_runtime(),
        )
    )

    assert resultado == {
        "resposta_especialista": resposta.resposta,
        "erro": None,
    }
    agente.ainvoke.assert_awaited_once()


def test_visualizacao_bloqueia_perfil_sem_permissao(
    monkeypatch,
) -> None:
    agente = SimpleNamespace(ainvoke=AsyncMock())
    monkeypatch.setattr(nodes, "visualizacoes_gestor", agente)

    resultado = asyncio.run(
        nodes.executar_visualizacao(
            criar_estado("tecnico"),
            criar_runtime(),
        )
    )

    assert resultado["erro"] is None
    assert "permissao" in resultado["resposta_especialista"]
    agente.ainvoke.assert_not_awaited()


def test_executar_feedback(monkeypatch) -> None:
    resposta = FeedbackResultado(
        agente="feedback",
        resposta="Feedback recebido.",
        status="SUCESSO",
    )
    agente = SimpleNamespace(
        ainvoke=AsyncMock(
            return_value={"structured_response": resposta}
        )
    )
    monkeypatch.setattr(nodes, "feedback", agente)

    resultado = asyncio.run(
        nodes.executar_feedback(
            criar_estado("solicitante"),
            criar_runtime(),
        )
    )

    assert resultado == {
        "resposta_especialista": resposta.resposta,
        "erro": None,
    }
    agente.ainvoke.assert_awaited_once()


def test_especialista_rejeita_resposta_incompativel(
    monkeypatch,
) -> None:
    agente = SimpleNamespace(
        ainvoke=AsyncMock(
            return_value={"structured_response": {}}
        )
    )
    monkeypatch.setattr(nodes, "feedback", agente)

    resultado = asyncio.run(
        nodes.executar_feedback(
            criar_estado(),
            criar_runtime(),
        )
    )

    assert resultado["resposta_especialista"] == ""
    assert "incompativel" in resultado["erro"]


def test_workflow_possui_todos_os_especialistas() -> None:
    from app.graph.workflow import grafo

    nomes = set(grafo.get_graph().nodes)

    assert {
        "agente_faq",
        "agente_solicitacao",
        "agente_analytics",
        "agente_visualizacao",
        "agente_feedback",
    }.issubset(nomes)
