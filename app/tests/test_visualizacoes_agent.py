"""Registro, seleção e orçamento do agente, sem LLM ou bancos externos."""

import asyncio
import json
from typing import get_args
from unittest.mock import AsyncMock
from uuid import uuid4

from langchain.tools import tool
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import ValidationError
import pytest

from app.agents import visualizacao
from app.agents.agentsResult import VisualizacaoResultado
from app.agents.prompts.construtor import construir_visualizacoes_gestor
from app.schemas import UsuarioContexto
from app.schemas.visualizacao import StatusConsultaVisualizacao
from app.services.indicadores.gerais import databricks
from app.services.visualizacoes import ANALISES
from app.services.visualizacoes.limites import MAXIMO_CONSULTAS_POR_EXECUCAO
from app.tools.metricas_kpis import contexto as contexto_indicadores
from app.tools.visualizacoes import FERRAMENTAS_VISUALIZACOES


NOMES = {t.name for t in FERRAMENTAS_VISUALIZACOES}


@pytest.fixture(autouse=True)
def dependencias(monkeypatch):
    monkeypatch.setenv("LANGSMITH_TRACING", "false")
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "false")
    unidade, banco = AsyncMock(return_value=7), AsyncMock(return_value=[])
    monkeypatch.setattr(contexto_indicadores, "obter_unidade_id", unidade)
    monkeypatch.setattr(databricks, "executar_consulta", banco)
    return unidade, banco


def contexto():
    return {"usuario": UsuarioContexto(
        access_token="token-teste", usuario_id=10, nome_completo="Gestor", email="teste@example.com",
        tipo_acesso="gestor", cnpj_endereco="12345678000195",
    )}


def chamada(analise_id="VIS-01", **alteracoes):
    a = ANALISES[analise_id]
    args = {"analise_id": analise_id, "filtros": {}}
    if a.fonte.campo_periodo:
        args["periodo"] = {"inicio": "2026-10-01", "fim": "2026-10-04"}
        args["granularidade"] = "dia" if a.formato_dados == "serie_temporal" else None
    args.update(alteracoes)
    return {"name": f"consultar_visualizacao_{a.fonte.id}", "args": args}


class ModeloRoteiro(BaseChatModel):
    """Produz lotes e uma resposta estruturada a partir dos ToolMessages reais."""

    lotes: list[list[dict]]

    @property
    def _llm_type(self):
        return "roteiro-visualizacao"

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        inicio = max((i for i, m in enumerate(messages) if isinstance(m, HumanMessage)), default=-1)
        atuais = messages[inicio + 1:]
        lotes_emitidos = sum(
            isinstance(m, AIMessage) and any(c["name"] in NOMES | {"buscar_historico"} for c in m.tool_calls)
            for m in atuais
        )
        if lotes_emitidos < len(self.lotes):
            prefixo = str(uuid4())
            mensagem = AIMessage(content="", tool_calls=[
                {**c, "id": f"{prefixo}-{i}", "type": "tool_call"}
                for i, c in enumerate(self.lotes[lotes_emitidos])
            ])
        else:
            resultados = [json.loads(m.content) for m in atuais if isinstance(m, ToolMessage) and m.name in NOMES]
            validos = [r for r in resultados if r["status"] in {"SUCESSO", "SUCESSO_PARCIAL"} and r["dados"] is not None]
            selecao = None
            if validos:
                meta = validos[0]["metadados"]
                selecao = {"analise_id": meta["analise_id"], "consulta_id": meta["consulta_id"]}
                status = "SUCESSO_PARCIAL" if any(r["status"] != "SUCESSO" for r in resultados) else "SUCESSO"
            else:
                status = resultados[-1]["status"] if resultados else "AGUARDANDO_INFORMACAO"
            resposta = VisualizacaoResultado(
                agente="visualizacao", resposta="Consulta processada." if resultados else "Qual período deseja analisar?",
                status=status, visualizacao=selecao,
            )
            mensagem = AIMessage(content="", tool_calls=[{
                "name": "VisualizacaoResultado", "args": resposta.model_dump(mode="json"),
                "id": str(uuid4()), "type": "tool_call",
            }])
        return ChatResult(generations=[ChatGeneration(message=mensagem)])


def executar(agente):
    return asyncio.run(agente.ainvoke({"messages": [HumanMessage(content="Mostre uma visualização.")]}, context=contexto()))


@pytest.mark.parametrize("concorrente", [False, True])
def test_no_captura_sdk_real_com_escopo_isolado(monkeypatch, dependencias, concorrente):
    from types import SimpleNamespace
    from app.graph import nos
    unidade, banco = dependencias
    unidade.side_effect = lambda usuario: 7 if usuario.usuario_id == 10 else 8
    async def linhas(_sql, parametros, **kwargs):
        valor = 2 if parametros["unidade_id"] == 7 else 3
        return [{"data_referencia": "2026-10-02", "valor": str(valor), "qtd_registros": str(valor)}]
    banco.side_effect = linhas
    agente = visualizacao.criar_agente_visualizacao(ModeloRoteiro(lotes=[[chamada()] * 3]), construir_visualizacoes_gestor())
    monkeypatch.setattr(nos, "visualizacoes_gestor", agente)
    async def executar_nos():
        async def um(usuario_id):
            ctx = contexto()
            ctx["usuario"] = ctx["usuario"].model_copy(update={"usuario_id": usuario_id})
            ctx.update(session_id=f"sessao-{usuario_id}", turno_id=f"turno-{usuario_id}")
            return await nos.executar_visualizacao({
                "messages": [HumanMessage(content="Mostre as OS criadas por dia.")],
                "perfil": "gestor", "user_id": usuario_id,
            }, SimpleNamespace(context=ctx))
        return await asyncio.gather(um(10), um(20)) if concorrente else [await um(10), await um(20)]
    resultados = asyncio.run(executar_nos())
    assert unidade.await_count == banco.await_count == 6
    assert resultados[0]["visualizacao_execucao_id"] != resultados[1]["visualizacao_execucao_id"]
    for usuario_id, unidade_id, valor, saida in zip((10, 20), (7, 8), (2, 3), resultados):
        assert saida["erro"] is None and len(saida["consultas_visualizacao"]) == 3
        candidata = saida["visualizacao_candidata"]
        assert candidata["usuario_id"] == usuario_id and candidata["unidade_id"] == unidade_id
        assert candidata["resultado"]["dados"]["pontos"][1]["valor"] == valor
        assert candidata in saida["consultas_visualizacao"]
        assert len(saida["evidencias"]) == 3


def test_fabrica_injeta_as_seis_tools_historico_schema_e_limite(monkeypatch):
    monkeypatch.setattr(visualizacao, "create_agent", lambda **kwargs: kwargs)
    agente = visualizacao.criar_agente_visualizacao(object(), "instrução")
    assert {t.name for t in agente["tools"]} == NOMES | {"buscar_historico"}
    assert len(agente["tools"]) == 7
    assert agente["response_format"] is VisualizacaoResultado
    assert agente["system_prompt"] == "instrução"
    assert len(agente["middleware"]) == 1
    assert agente["middleware"][0].run_limit == MAXIMO_CONSULTAS_POR_EXECUCAO == 3


def test_extensoes_nao_substituem_tools_canonicas_com_mesmo_nome(monkeypatch):
    monkeypatch.setattr(visualizacao, "create_agent", lambda **kwargs: kwargs)
    falsa = FERRAMENTAS_VISUALIZACOES[0].model_copy(update={"description": "substituta"})
    agente = visualizacao.criar_agente_visualizacao(object(), "instrução", ferramentas=[falsa, visualizacao.buscar_historico])
    assert len(agente["tools"]) == 7
    assert agente["tools"][0] is FERRAMENTAS_VISUALIZACOES[0]


def test_registro_real_contem_tools_apenas_no_especialista_gestor():
    from app.agents.registro import AGENTES_POR_PERFIL, visualizacoes_gestor
    assert set(AGENTES_POR_PERFIL["visualizacao"]) == {"gestor"}
    assert AGENTES_POR_PERFIL["visualizacao"]["gestor"] is visualizacoes_gestor
    assert "tools" in visualizacoes_gestor.get_graph().nodes


def test_prompt_usa_catalogo_canonico_e_consulta_direta_sem_exemplos_numericos_inventados():
    prompt = construir_visualizacoes_gestor()
    for a in ANALISES.values():
        assert f"{a.id} | consultar_visualizacao_{a.fonte.id} | {a.titulo}" in prompt
    assert "Você próprio consulta o Databricks" in prompt
    assert "uma visualização por resposta" in prompt and "no máximo 3 chamadas" in prompt
    assert "AGUARDANDO_INFORMACAO" in prompt and "fim é exclusivo" in prompt
    assert "buscar_historico apenas para entender o contexto" in prompt
    assert "sem ranking entre unidades" in prompt and "0–100" in prompt
    assert "não prometa tempo real" in prompt.lower()
    assert "trabalhe prioritariamente sobre resultados validados" not in prompt.lower()
    assert "Saída completa" not in prompt


@pytest.mark.parametrize("status", get_args(StatusConsultaVisualizacao))
def test_contrato_aceita_status_analiticos_e_so_sucesso_seleciona(status):
    referencia = {"analise_id": "VIS-01", "consulta_id": "consulta-teste"}
    sucesso = status in {"SUCESSO", "SUCESSO_PARCIAL"}
    resultado = VisualizacaoResultado(
        agente="visualizacao", resposta="Resultado da consulta.", status=status,
        visualizacao=referencia if sucesso else None,
    )
    assert (resultado.visualizacao is not None) == sucesso
    assert VisualizacaoResultado.model_validate_json(resultado.model_dump_json()) == resultado
    with pytest.raises(ValidationError, match="referência"):
        VisualizacaoResultado(
            agente="visualizacao", resposta="Resultado.", status=status,
            visualizacao=None if sucesso else referencia,
        )


@pytest.mark.parametrize("status", ["AGUARDANDO_INFORMACAO", "ERRO_MODELO"])
def test_esclarecimento_ou_falha_de_geracao_nao_inventa_referencia(status):
    assert VisualizacaoResultado(agente="visualizacao", resposta="Preciso esclarecer.", status=status).visualizacao is None


@pytest.mark.parametrize("mudanca", [
    {"visualizacao": [{"analise_id": "VIS-01", "consulta_id": "a"}, {"analise_id": "VIS-02", "consulta_id": "b"}]},
    {"visualizacoes": []}, {"dados": []}, {"configuracao": {}},
    {"visualizacao": {"analise_id": "VIS-01", "consulta_id": "a", "dados": [10]}},
    {"visualizacao": {"analise_id": "VIS-01", "consulta_id": " "}},
    {"visualizacao": {"analise_id": "VIS-01", "consulta_id": " a"}},
    {"resposta": " "}, {"agente": "visualization_agent"},
])
def test_uma_selecao_nao_aceita_lista_dados_inventados_ou_identificador_alterado(mudanca):
    dados = {"agente": "visualizacao", "resposta": "Resultado.", "status": "SUCESSO",
             "visualizacao": {"analise_id": "VIS-01", "consulta_id": "a"}}
    with pytest.raises(ValidationError):
        VisualizacaoResultado.model_validate({**dados, **mudanca})


def test_agente_real_seleciona_referencia_retornada_pela_tool(dependencias):
    unidade, banco = dependencias
    banco.return_value = [{"data_referencia": "2026-10-02", "valor": "3", "qtd_registros": "3"}]
    agente = visualizacao.criar_agente_visualizacao(ModeloRoteiro(lotes=[[chamada()]]), construir_visualizacoes_gestor())
    resultado = executar(agente)
    resposta = resultado["structured_response"]
    consulta = next(json.loads(m.content) for m in resultado["messages"] if isinstance(m, ToolMessage) and m.name in NOMES)
    assert resposta.status == "SUCESSO"
    assert resposta.visualizacao.consulta_id == consulta["metadados"]["consulta_id"]
    assert resposta.visualizacao.analise_id == "VIS-01"
    assert "dados" not in resposta.model_dump()
    assert [p["valor"] for p in consulta["dados"]["pontos"]] == [0, 3, 0]
    unidade.assert_awaited_once()
    banco.assert_awaited_once()


@pytest.mark.parametrize("paralelo", [True, False])
def test_limite_tres_e_compartilhado_e_aplicado_antes_de_executar_lote(dependencias, paralelo):
    unidade, banco = dependencias
    chamadas = [chamada(i) for i in ("VIS-01", "VIS-02", "VIS-09", "VIS-03")]
    lotes = [chamadas] if paralelo else [[c] for c in chamadas]
    agente = visualizacao.criar_agente_visualizacao(ModeloRoteiro(lotes=lotes), construir_visualizacoes_gestor())
    resultado = executar(agente)
    assert unidade.await_count == banco.await_count == 3
    erros = [m for m in resultado["messages"] if isinstance(m, ToolMessage) and m.status == "error"]
    assert len(erros) == 1
    erro = json.loads(erros[0].content)
    assert erro["status"] == "ERRO_VALIDACAO" and erro["dados"] is None
    assert "Limite de consultas" in erro["mensagem"]
    assert resultado["structured_response"].visualizacao is None


def test_tentativas_com_argumentos_invalidos_tambem_consumem_orcamento(dependencias):
    unidade, banco = dependencias
    invalida = chamada(analise_id="VIS-01")
    invalida["args"]["analise_id"] = "VIS-99"
    agente = visualizacao.criar_agente_visualizacao(
        ModeloRoteiro(lotes=[[invalida], [invalida], [chamada()], [chamada()]]), construir_visualizacoes_gestor(),
    )
    resultado = executar(agente)
    assert unidade.await_count == banco.await_count == 1
    erros = [m for m in resultado["messages"] if isinstance(m, ToolMessage) and m.status == "error"]
    assert len(erros) == 3 and "Limite de consultas" in erros[-1].content


def test_historico_e_resposta_estruturada_nao_consumem_orcamento_analitico(monkeypatch, dependencias):
    unidade, banco = dependencias
    @tool("buscar_historico")
    async def historico(busca: str) -> str:
        """Histórico de teste sem acesso externo."""
        return "Contexto da conversa, sem dados atuais."
    monkeypatch.setattr(visualizacao, "buscar_historico", historico)
    lotes = [[{"name": "buscar_historico", "args": {"busca": "visualização"}}], [chamada()] * 3]
    agente = visualizacao.criar_agente_visualizacao(ModeloRoteiro(lotes=lotes), construir_visualizacoes_gestor())
    resultado = executar(agente)
    assert unidade.await_count == banco.await_count == 3
    assert resultado["structured_response"].status == "SEM_RESULTADO"
    assert not any(isinstance(m, ToolMessage) and m.status == "error" for m in resultado["messages"])


@pytest.mark.parametrize("concorrente", [False, True])
def test_orcamento_e_isolado_por_execucao_do_mesmo_agente(dependencias, concorrente):
    unidade, banco = dependencias
    agente = visualizacao.criar_agente_visualizacao(ModeloRoteiro(lotes=[[chamada()] * 3]), construir_visualizacoes_gestor())
    async def duas_execucoes():
        async def uma():
            return await agente.ainvoke({"messages": [HumanMessage(content="Visualização.")]}, context=contexto())
        if concorrente:
            return await asyncio.gather(uma(), uma())
        return [await uma(), await uma()]
    resultados = asyncio.run(duas_execucoes())
    assert unidade.await_count == banco.await_count == 6
    assert all(r["structured_response"].status == "SEM_RESULTADO" for r in resultados)
