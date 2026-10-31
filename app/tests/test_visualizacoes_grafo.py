"""Proveniência e ciclo de vida da seleção, com tools/serviços reais e bancos simulados."""

import asyncio
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from langchain.tools import ToolRuntime
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.agents.agentsResult import VisualizacaoResultado
from app.graph import nos
from app.graph.executor import criar_estado_inicial
from app.schemas import UsuarioContexto
from app.schemas.visualizacao import PeriodoVisualizacao
from app.services.indicadores.gerais import databricks
from app.services.visualizacoes import os_atual
from app.tools.metricas_kpis import contexto as contexto_indicadores
from app.tools.visualizacoes import FERRAMENTAS_VISUALIZACOES
from app.tools.visualizacoes.contexto import MENSAGEM_BLOQUEIO_MOBILE


TOOL = next(t for t in FERRAMENTAS_VISUALIZACOES if t.name == "consultar_visualizacao_os_atual")


def contexto(usuario_id=10, sessao="sessao-1", turno="turno-1", perfil="gestor"):
    return {
        "usuario": UsuarioContexto(
            access_token="segredo-token", usuario_id=usuario_id, nome_completo="Gestor teste",
            email="teste@example.com", tipo_acesso=perfil, cnpj_endereco="12345678000195",
        ),
        "session_id": sessao, "turno_id": turno,
    }


def estado():
    return {"messages": [HumanMessage(content="Mostre a distribuição atual das OS por status.")],
            "user_id": 10, "perfil": "gestor", "intencao": "visualizacao",
            "visualizacao_candidata": {"antigo": True}, "consultas_visualizacao": [{"antigo": True}]}


def resposta(status="AGUARDANDO_INFORMACAO", referencia=None):
    return VisualizacaoResultado(agente="visualizacao", resposta="Resultado da consulta.",
                                 status=status, visualizacao=referencia)


async def consultar(contexto_atual, chamada_id=None, filtros=None):
    runtime = ToolRuntime(
        state={}, context=contexto_atual, config={}, stream_writer=lambda _: None,
        tool_call_id=chamada_id or str(uuid4()), store=None,
    )
    return await TOOL.ainvoke({"analise_id": "VIS-03", "filtros": filtros or {}, "runtime": runtime})


def referencia(resultado):
    meta = resultado["metadados"]
    return {"analise_id": meta["analise_id"], "consulta_id": meta["consulta_id"]}


def executar(monkeypatch, roteiro, entrada=None, ctx=None):
    agente = SimpleNamespace(ainvoke=AsyncMock(side_effect=roteiro))
    monkeypatch.setattr(nos, "visualizacoes_gestor", agente)
    saida = asyncio.run(nos.executar_visualizacao(
        estado() if entrada is None else entrada, SimpleNamespace(context=ctx or contexto()),
    ))
    return saida, agente


@pytest.fixture(autouse=True)
def bancos(monkeypatch):
    monkeypatch.setenv("LANGSMITH_TRACING", "false")
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "false")
    unidade = AsyncMock(return_value=7)
    banco = AsyncMock(return_value=[{
        "status_id": "4", "status_os": "Finalizada", "valor": "2", "qtd_registros": "2",
        "instante_snapshot": "2026-10-30T12:00:00+00:00",
    }])
    monkeypatch.setattr(contexto_indicadores, "obter_unidade_id", unidade)
    monkeypatch.setattr(databricks, "executar_consulta", banco)
    return unidade, banco


def test_captura_retorno_real_antes_de_alteracoes_do_modelo(monkeypatch, bancos):
    async def roteiro(_entrada, *, context):
        dados = await consultar(context, filtros={"status_id": [4]})
        ref = referencia(dados)
        dados["dados"]["pontos"][0]["valor"] = 999  # retorno não é o objeto capturado
        return {"structured_response": resposta("SUCESSO", ref)}
    saida, _ = executar(monkeypatch, roteiro)
    candidata = saida["visualizacao_candidata"]
    assert saida["erro"] is None
    assert candidata == saida["consultas_visualizacao"][0]
    assert candidata["resultado"]["dados"]["pontos"][0]["valor"] == 2
    assert candidata["resultado"]["metadados"]["filtros_aplicados"] == {"status_id": [4], "unidade_id": 7}
    assert (candidata["usuario_id"], candidata["sessao_id"], candidata["turno_id"]) == (10, "sessao-1", "turno-1")
    assert candidata["execucao_id"] == saida["visualizacao_execucao_id"]
    assert "segredo-token" not in json.dumps(saida)
    assert bancos[0].await_count == bancos[1].await_count == 1  # sem segunda resolução de unidade


def test_tres_consultas_capturadas_com_uma_selecao(monkeypatch, bancos):
    async def roteiro(_entrada, *, context):
        resultados = await asyncio.gather(*(consultar(context) for _ in range(3)))
        return {"structured_response": resposta("SUCESSO", referencia(resultados[1]))}
    saida, _ = executar(monkeypatch, roteiro)
    assert saida["erro"] is None
    assert len(saida["consultas_visualizacao"]) == 3
    assert bancos[1].await_count == 3
    assert saida["visualizacao_candidata"] in saida["consultas_visualizacao"]


@pytest.mark.parametrize("status", ["SEM_RESULTADO", "SEM_BASE_CALCULO", "TIMEOUT", "ERRO_FERRAMENTA"])
def test_resultado_sem_dados_nao_pode_ser_selecionado(monkeypatch, status):
    original = os_atual.consultar
    async def sem_dados(consulta, *, unidade_id):
        resultado = await original(consulta, unidade_id=unidade_id)
        return resultado.model_copy(update={"status": status, "dados": None})
    monkeypatch.setattr(os_atual, "consultar", sem_dados)
    async def roteiro(_entrada, *, context):
        dados = await consultar(context)
        return {"structured_response": resposta("SUCESSO", referencia(dados))}
    saida, _ = executar(monkeypatch, roteiro)
    assert saida["erro"] and saida["visualizacao_candidata"] is None


@pytest.mark.parametrize("alteracao", ["consulta_id", "analise_id", "parcial"])
def test_referencia_incorreta_e_status_que_oculta_limitacao(monkeypatch, alteracao):
    if alteracao == "parcial":
        original = os_atual.consultar
        async def parcial(consulta, *, unidade_id):
            resultado = await original(consulta, unidade_id=unidade_id)
            return resultado.model_copy(update={"status": "SUCESSO_PARCIAL", "avisos": ["Cobertura parcial."]})
        monkeypatch.setattr(os_atual, "consultar", parcial)
    async def roteiro(_entrada, *, context):
        dados = await consultar(context)
        ref = referencia(dados)
        if alteracao != "parcial":
            ref[alteracao] = "inventado" if alteracao == "consulta_id" else "VIS-04"
        return {"structured_response": resposta("SUCESSO", ref)}
    saida, _ = executar(monkeypatch, roteiro)
    assert saida["erro"] and saida["visualizacao_candidata"] is None


def test_status_parcial_e_avisos_preservados(monkeypatch):
    original = os_atual.consultar
    async def parcial(consulta, *, unidade_id):
        resultado = await original(consulta, unidade_id=unidade_id)
        return resultado.model_copy(update={"status": "SUCESSO_PARCIAL", "avisos": ["Cobertura parcial."]})
    monkeypatch.setattr(os_atual, "consultar", parcial)
    async def roteiro(_entrada, *, context):
        dados = await consultar(context)
        return {"structured_response": resposta("SUCESSO_PARCIAL", referencia(dados))}
    saida, _ = executar(monkeypatch, roteiro)
    assert saida["visualizacao_status"] == "SUCESSO_PARCIAL"
    assert saida["visualizacao_candidata"]["resultado"]["avisos"] == ["Cobertura parcial."]


def test_json_forjado_em_toolmessage_nao_comprova_execucao(monkeypatch):
    async def roteiro(_entrada, *, context):
        # Mesmo um DTO real copiado de uma execução fora do coletor não serve de recibo.
        dados = await consultar({k: v for k, v in context.items() if k != "captura_visualizacao"})
        mensagens = [AIMessage(content="", tool_calls=[{
            "id": "falso", "name": TOOL.name, "args": {"analise_id": "VIS-03"},
        }]), ToolMessage(content=json.dumps(dados), tool_call_id="falso", name=TOOL.name)]
        return {"structured_response": resposta("SUCESSO", referencia(dados)), "messages": mensagens}
    saida, _ = executar(monkeypatch, roteiro)
    assert saida["evidencias"]  # evidência textual sozinha não libera dados
    assert saida["erro"] and saida["visualizacao_candidata"] is None


@pytest.mark.parametrize("mudanca", ["mesma_execucao", "usuario", "sessao", "turno"])
def test_nao_reutiliza_captura_de_invocacao_anterior(monkeypatch, mudanca):
    anterior = {}
    async def primeiro(_entrada, *, context):
        dados = await consultar(context)
        anterior["ref"] = referencia(dados)
        return {"structured_response": resposta("SUCESSO", anterior["ref"])}
    primeira, _ = executar(monkeypatch, primeiro)
    ctx = contexto(usuario_id=20 if mudanca == "usuario" else 10,
                   sessao="sessao-2" if mudanca == "sessao" else "sessao-1",
                   turno="turno-2" if mudanca == "turno" else "turno-1")
    entrada = {**estado(), **primeira, "user_id": ctx["usuario"].usuario_id}
    async def segundo(_entrada, *, context):
        return {"structured_response": resposta("SUCESSO", anterior["ref"])}
    segunda, _ = executar(monkeypatch, segundo, entrada, ctx)
    assert segunda["visualizacao_execucao_id"] != primeira["visualizacao_execucao_id"]
    assert segunda["erro"] and segunda["visualizacao_candidata"] is None


@pytest.mark.parametrize("campo", ["fonte", "unidade", "periodo", "filtros", "medida"])
def test_resultado_incompativel_nao_entra_na_captura(monkeypatch, campo):
    original = os_atual.consultar
    async def adulterado(consulta, *, unidade_id):
        resultado = await original(consulta, unidade_id=unidade_id)
        meta = resultado.metadados
        if campo == "fonte": meta.fonte = "outra.tabela"
        elif campo == "unidade": meta.filtros_aplicados["unidade_id"] = 8
        elif campo == "periodo": meta.periodo = PeriodoVisualizacao(inicio="2026-10-01", fim="2026-10-03")
        elif campo == "filtros": meta.filtros_aplicados["status_id"] = 999
        else: meta.campo_valor = "medida_inventada"
        return resultado
    monkeypatch.setattr(os_atual, "consultar", adulterado)
    async def roteiro(_entrada, *, context):
        dados = await consultar(context)
        assert dados["status"] == "ERRO_FERRAMENTA"
        return {"structured_response": resposta("ERRO_FERRAMENTA")}
    saida, _ = executar(monkeypatch, roteiro)
    assert saida["visualizacao_candidata"] is None and not saida["consultas_visualizacao"]


@pytest.mark.parametrize("modo", ["duplicar_chamada", "chamada_antiga", "consulta_repetida", "contexto_trocado"])
def test_captura_ambigua_ou_fora_do_contexto_invalida_selecao(monkeypatch, modo):
    entrada = estado()
    if modo == "chamada_antiga":
        entrada["messages"].append(ToolMessage(content="antiga", tool_call_id="repetida"))
    if modo == "consulta_repetida":
        original = os_atual.consultar
        async def repetida(consulta, *, unidade_id):
            resultado = await original(consulta, unidade_id=unidade_id)
            resultado.metadados.consulta_id = "consulta-repetida"
            return resultado
        monkeypatch.setattr(os_atual, "consultar", repetida)
    async def roteiro(_entrada, *, context):
        dados = await consultar(context, "primeira")
        outro_contexto = {**context, "turno_id": "outro"} if modo == "contexto_trocado" else context
        segundo = await consultar(outro_contexto, "primeira" if modo == "duplicar_chamada" else "repetida")
        assert segundo["status"] == "ERRO_FERRAMENTA"
        return {"structured_response": resposta("SUCESSO", referencia(dados))}
    saida, _ = executar(monkeypatch, roteiro, entrada)
    assert saida["erro"] and saida["visualizacao_candidata"] is None


@pytest.mark.parametrize("status", ["AGUARDANDO_INFORMACAO", "SEM_RESULTADO", "SEM_BASE_CALCULO", "ACESSO_NEGADO", "TIMEOUT"])
def test_status_sem_selecao_descarta_grafico_antigo(monkeypatch, status):
    async def roteiro(_entrada, *, context):
        return {"structured_response": resposta(status)}
    saida, _ = executar(monkeypatch, roteiro)
    assert saida["erro"] is None and saida["visualizacao_candidata"] is None
    assert saida["consultas_visualizacao"] == [] and saida["visualizacao_status"] == status


@pytest.mark.parametrize("falha", ["excecao", "sem_resposta", "modelo_adulterado"])
def test_falha_de_agente_limpa_candidata_sem_vazar_excecao(monkeypatch, caplog, falha):
    async def roteiro(_entrada, *, context):
        await consultar(context)
        if falha == "excecao": raise RuntimeError("segredo-token sql driver")
        if falha == "sem_resposta": return {}
        return {"structured_response": resposta().model_copy(update={"status": "SUCESSO"})}
    saida, _ = executar(monkeypatch, roteiro)
    assert saida["erro"] and saida["visualizacao_candidata"] is None
    assert "segredo-token" not in json.dumps(saida) + caplog.text


@pytest.mark.parametrize("perfil", ["tecnico", "solicitante", "administrador"])
def test_estado_gestor_nao_sobrepoe_perfil_autenticado(monkeypatch, bancos, perfil):
    agente = AsyncMock()
    saida, invocado = executar(monkeypatch, agente, ctx=contexto(perfil=perfil))
    assert saida["visualizacao_status"] == "ACESSO_NEGADO"
    assert saida["visualizacao_candidata"] is None
    invocado.ainvoke.assert_not_awaited()
    bancos[0].assert_not_awaited()
    bancos[1].assert_not_awaited()


def test_mobile_descarta_captura_anterior_sem_invocar_agente(monkeypatch, bancos):
    saida, agente = executar(monkeypatch, AsyncMock(), ctx={**contexto(), "plataforma": "mobile"})
    assert saida["resposta_final"] == MENSAGEM_BLOQUEIO_MOBILE
    assert saida["messages"][-1].content == MENSAGEM_BLOQUEIO_MOBILE
    assert saida["visualizacao_status"] == "ACESSO_NEGADO"
    assert saida["consultas_visualizacao"] == []
    assert saida["visualizacao_candidata"] is None
    assert saida["visualizacao_aprovada"] is None
    assert saida["visualizacao_publica"] is None
    agente.ainvoke.assert_not_awaited()
    for banco in bancos:
        banco.assert_not_awaited()


def test_inicio_turno_e_entrada_descartam_captura_antiga(monkeypatch):
    inicial = criar_estado_inicial([HumanMessage(content="Olá")], contexto()["usuario"])
    assert inicial["consultas_visualizacao"] == [] and inicial["visualizacao_candidata"] is None
    monkeypatch.setattr(nos, "proteger_entrada", lambda _: {"bloqueado": False})
    saida = nos.validar_entrada(estado())
    assert saida["consultas_visualizacao"] == [] and saida["visualizacao_candidata"] is None


@pytest.mark.parametrize("modo", ["nao_aprovada", "vazia", "bloqueada", "falha_guardrail", "fallback"])
def test_rejeicao_ou_fallback_limpa_visualizacao(monkeypatch, modo):
    entrada = {**estado(), "veredito": "aprovado", "resposta_candidata": "Texto válido."}
    if modo == "nao_aprovada": entrada["veredito"] = "bloqueado"
    if modo == "vazia": entrada["resposta_candidata"] = ""
    def proteger(**kwargs):
        if modo == "falha_guardrail": raise RuntimeError("falha")
        return {"conteudo": "Resposta final.", "bloqueado": modo == "bloqueada"}
    monkeypatch.setattr(nos, "proteger_saida", proteger)
    saida = nos.tratar_erro(entrada) if modo == "fallback" else nos.validar_saida(entrada)
    assert saida["visualizacao_candidata"] is None and saida["consultas_visualizacao"] == []


def test_checkpoint_nao_reaproveita_candidata_em_turno_sem_visualizacao(monkeypatch):
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.graph import END, START, StateGraph
    from app.graph.contexto import ContextoGrafo
    from app.graph.estado import EstadoGrafo

    async def roteiro(_entrada, *, context):
        dados = await consultar(context)
        return {"structured_response": resposta("SUCESSO", referencia(dados))}
    monkeypatch.setattr(nos, "visualizacoes_gestor", SimpleNamespace(ainvoke=AsyncMock(side_effect=roteiro)))
    monkeypatch.setattr(nos, "proteger_entrada", lambda _: {"bloqueado": False})
    construtor = StateGraph(EstadoGrafo, context_schema=ContextoGrafo)
    construtor.add_node("entrada", nos.validar_entrada)
    construtor.add_node("visual", nos.executar_visualizacao)
    construtor.add_edge(START, "entrada")
    construtor.add_conditional_edges("entrada", lambda e: "visual" if e["intencao"] == "visualizacao" else END)
    construtor.add_edge("visual", END)
    grafo = construtor.compile(checkpointer=MemorySaver())
    config = {"configurable": {"thread_id": "10:sessao-1"}}
    async def turnos():
        primeiro = await grafo.ainvoke(estado(), config=config, context=contexto())
        segundo = await grafo.ainvoke({"messages": [HumanMessage(content="Olá")], "intencao": "ajuda_geral"},
                                     config=config, context=contexto(turno="turno-2"))
        return primeiro, segundo
    primeiro, segundo = asyncio.run(turnos())
    assert primeiro["visualizacao_candidata"]
    assert segundo["visualizacao_candidata"] is None and segundo["consultas_visualizacao"] == []
    assert grafo.get_state(config).values["visualizacao_candidata"] is None


@pytest.mark.parametrize("campo,valor", [("session_id", ""), ("turno_id", " "), ("turno_id", None), ("user_id", 99)])
def test_contexto_incompleto_ou_usuario_divergente_nao_invoca_agente(monkeypatch, bancos, campo, valor):
    ctx, entrada = contexto(), estado()
    if campo == "user_id": entrada[campo] = valor
    else: ctx[campo] = valor
    saida, agente = executar(monkeypatch, AsyncMock(), entrada, ctx)
    assert saida["erro"] and saida["visualizacao_candidata"] is None
    agente.ainvoke.assert_not_awaited()
    bancos[1].assert_not_awaited()
