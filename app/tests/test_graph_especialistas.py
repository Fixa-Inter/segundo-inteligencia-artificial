import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from langchain_core.messages import HumanMessage

from app.agents.agentsResult import (
    IndicadoresResultado,
    RetornoUsuarioResultado,
    VisualizacaoResultado,
)
from app.graph import nos
from app.schemas import UsuarioContexto


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
    resposta = IndicadoresResultado(
        agente="analytics",
        resposta="Foram encontrados 10 chamados.",
        status="SUCESSO",
    )
    agente = SimpleNamespace(
        ainvoke=AsyncMock(
            return_value={"structured_response": resposta}
        )
    )
    monkeypatch.setattr(nos, "indicadores_gestor", agente)

    resultado = asyncio.run(
        nos.executar_indicadores(
            criar_estado(),
            criar_runtime(),
        )
    )

    assert resultado == {
        "evidencias": [],
        "resposta_especialista": resposta.resposta,
        "erro": None,
    }
    agente.ainvoke.assert_awaited_once()


def test_analytics_bloqueia_perfil_sem_permissao(
    monkeypatch,
) -> None:
    agente = SimpleNamespace(ainvoke=AsyncMock())
    monkeypatch.setattr(nos, "indicadores_gestor", agente)

    resultado = asyncio.run(
        nos.executar_indicadores(
            criar_estado("solicitante"),
            criar_runtime(),
        )
    )

    assert resultado["erro"] is None
    assert "permissao" in resultado["resposta_especialista"]
    agente.ainvoke.assert_not_awaited()


def test_administrador_acessa_indicadores_gerenciais(monkeypatch) -> None:
    resposta = IndicadoresResultado(agente="analytics", resposta="Há 10 OS na unidade.", status="SUCESSO")
    agente = SimpleNamespace(ainvoke=AsyncMock(return_value={"structured_response": resposta}))
    monkeypatch.setattr(nos, "indicadores_administrador", agente)

    resultado = asyncio.run(nos.executar_indicadores(
        criar_estado("administrador"), criar_runtime(),
    ))

    assert resultado["erro"] is None
    assert resultado["resposta_especialista"] == resposta.resposta
    agente.ainvoke.assert_awaited_once()


def test_visualizacao_rejeita_sucesso_sem_consulta_executada(monkeypatch) -> None:
    resposta = VisualizacaoResultado(
        agente="visualizacao",
        resposta="Use um grafico de barras.",
        status="SUCESSO",
        visualizacao={"analise_id": "VIS-08", "consulta_id": "consulta-teste"},
    )
    agente = SimpleNamespace(
        ainvoke=AsyncMock(
            return_value={"structured_response": resposta}
        )
    )
    monkeypatch.setattr(nos, "visualizacoes_gestor", agente)
    runtime = criar_runtime()
    runtime.context.update({
        "usuario": UsuarioContexto(
            access_token="token-teste", usuario_id=10, nome_completo="Gestor",
            email="teste@example.com", tipo_acesso="gestor", cnpj_endereco="12345678000195",
        ),
        "session_id": "sessao-teste", "turno_id": "turno-teste",
    })

    resultado = asyncio.run(
        nos.executar_visualizacao(
            criar_estado(),
            runtime,
        )
    )

    assert resultado["erro"]
    assert resultado["visualizacao_candidata"] is None
    assert resultado["resposta_especialista"] == ""
    agente.ainvoke.assert_awaited_once()


@pytest.mark.parametrize("perfil", ["tecnico", "administrador"])
def test_visualizacao_bloqueia_perfil_sem_permissao(
    monkeypatch, perfil,
) -> None:
    agente = SimpleNamespace(ainvoke=AsyncMock())
    monkeypatch.setattr(nos, "visualizacoes_gestor", agente)

    resultado = asyncio.run(
        nos.executar_visualizacao(
            criar_estado(perfil),
            criar_runtime(),
        )
    )

    assert resultado["erro"] is None
    assert "permissao" in resultado["resposta_especialista"]
    agente.ainvoke.assert_not_awaited()


def test_executar_feedback(monkeypatch) -> None:
    resposta = RetornoUsuarioResultado(
        agente="feedback",
        resposta="Feedback recebido.",
        status="SUCESSO",
    )
    agente = SimpleNamespace(
        ainvoke=AsyncMock(
            return_value={"structured_response": resposta}
        )
    )
    monkeypatch.setattr(nos, "feedback", agente)

    resultado = asyncio.run(
        nos.executar_retorno_usuario(
            criar_estado("solicitante"),
            criar_runtime(),
        )
    )

    assert resultado == {
        "evidencias": [],
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
    monkeypatch.setattr(nos, "feedback", agente)

    resultado = asyncio.run(
        nos.executar_retorno_usuario(
            criar_estado(),
            criar_runtime(),
        )
    )

    assert resultado["resposta_especialista"] == ""
    assert "incompativel" in resultado["erro"]


def test_workflow_possui_todos_os_especialistas() -> None:
    from app.graph.fluxo import grafo

    nomes = set(grafo.get_graph().nodes)

    assert {
        "agente_faq",
        "agente_solicitacao",
        "agente_analytics",
        "agente_visualizacao",
        "agente_feedback",
    }.issubset(nomes)
