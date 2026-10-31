"""Julgamento, revisão e saída da visualização, sem modelos ou bancos externos."""

import asyncio
import copy
import json
from importlib import import_module
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from langchain.tools import ToolRuntime
from langchain_core.messages import HumanMessage

from app.agents.agentsResult import VisualizacaoResultado
from app.graph import fluxo, nos
from app.graph.executor import criar_estado_inicial
from app.schemas import UsuarioContexto
from app.services.indicadores.gerais import databricks
from app.tools.metricas_kpis import contexto as contexto_indicadores
from app.tools.visualizacoes import FERRAMENTAS_VISUALIZACOES

juiz = import_module("app.agents.juiz")


def avaliacao(veredito="aprovado", incompatibilidade=0.05, sem_suporte=0.05):
    return {"model": "modelo-teste", "answers": {
        "veredito": {"type": "choice", "choice": veredito, "confidence": 0.95},
        "motivo": {"type": "choice", "choice": "contradicao_evidencia" if veredito == "revisar" else "nenhum", "confidence": 0.95},
        "afirmacao_sem_suporte": {"type": "noul", "noul": sem_suporte},
        "correcao_textual": {"type": "noul", "noul": 0.95},
        "risco_grave": {"type": "noul", "noul": 0.05},
        "visualizacao_incompativel": {"type": "noul", "noul": incompatibilidade},
    }}


@pytest.fixture
def cenario(monkeypatch):
    monkeypatch.setenv("LANGSMITH_TRACING", "false")
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "false")
    ctx = {"usuario": UsuarioContexto(
        access_token="segredo-token-teste", usuario_id=10, nome_completo="Gestor",
        email="teste@example.com", tipo_acesso="gestor", cnpj_endereco="12345678000195",
    ), "session_id": "sessao-1", "turno_id": "turno-1"}
    runtime = SimpleNamespace(context=ctx)
    unidade = AsyncMock(return_value=7)
    banco = AsyncMock(return_value=[{
        "status_id": "4", "status_os": "Finalizada", "valor": "2", "qtd_registros": "2",
        "instante_snapshot": "2026-10-30T12:00:00+00:00",
    }])
    monkeypatch.setattr(contexto_indicadores, "obter_unidade_id", unidade)
    monkeypatch.setattr(databricks, "executar_consulta", banco)
    tool = next(t for t in FERRAMENTAS_VISUALIZACOES if t.name == "consultar_visualizacao_os_atual")
    async def executar(_entrada, *, context):
        injetado = ToolRuntime(state={}, context=context, config={}, stream_writer=lambda _: None,
                               tool_call_id="chamada-1", store=None)
        resultado = await tool.ainvoke({"analise_id": "VIS-03", "runtime": injetado})
        meta = resultado["metadados"]
        return {"structured_response": VisualizacaoResultado(
            agente="visualizacao", resposta="Há 2 OS finalizadas.", status="SUCESSO",
            visualizacao={"analise_id": meta["analise_id"], "consulta_id": meta["consulta_id"]},
        )}
    agente = SimpleNamespace(ainvoke=AsyncMock(side_effect=executar))
    monkeypatch.setattr(nos, "visualizacoes_gestor", agente)
    estado = {"messages": [HumanMessage(content="Mostre a distribuição atual das OS por status.")],
              "user_id": 10, "perfil": "gestor", "intencao": "visualizacao"}
    estado.update(asyncio.run(nos.executar_visualizacao(estado, runtime)))
    consultar = AsyncMock(return_value=avaliacao())
    monkeypatch.setattr(juiz, "consultar_jev", consultar)
    return SimpleNamespace(estado=estado, runtime=runtime, unidade=unidade, banco=banco,
                           julgar=consultar, agente=agente)


def julgar(c):
    return {**c.estado, **asyncio.run(juiz.julgar_resposta(c.estado, c.runtime))}


def test_juiz_avalia_dados_e_libera_somente_apos_protecao(cenario):
    c = cenario
    estado = julgar(c)
    assert estado["veredito"] == "aprovado"
    assert estado["visualizacao_aprovacao"] and estado["visualizacao_aprovada"] is None
    contexto, perguntas = c.julgar.await_args.args
    assert contexto["visualizacao"]["candidata"]["resultado"]["dados"]["pontos"][0]["valor"] == 2
    assert "visualizacao_incompativel" in perguntas
    assert not {"usuario_id", "sessao_id", "turno_id", "execucao_id"} & contexto["visualizacao"]["candidata"].keys()
    assert "segredo-token-teste" not in json.dumps(contexto)
    saida = nos.validar_saida(estado, c.runtime)
    assert saida["visualizacao_aprovada"] == c.estado["visualizacao_candidata"]["resultado"]
    assert saida["resposta_final"] == "Há 2 OS finalizadas."
    assert c.unidade.await_count == c.banco.await_count == 1


@pytest.mark.parametrize("campo", ["valor", "avisos", "consulta_id", "unidade", "fonte", "medida", "filtros", "execucao", "usuario", "sessao", "turno", "ferramenta", "duplicada", "ausente", "sem_dados", "status"])
def test_candidata_invalida_nao_chega_ao_jev(cenario, campo):
    c = cenario
    cand = c.estado["visualizacao_candidata"]
    if campo == "valor": cand["resultado"]["dados"]["pontos"][0]["valor"] = 999
    elif campo == "avisos": cand["resultado"]["avisos"].append("Inventado")
    elif campo == "consulta_id": cand["resultado"]["metadados"]["consulta_id"] = "inventada"
    elif campo == "unidade": cand["resultado"]["metadados"]["filtros_aplicados"]["unidade_id"] = 8
    elif campo == "fonte": cand["resultado"]["metadados"]["fonte"] = "outra.tabela"
    elif campo == "medida": cand["resultado"]["metadados"]["campo_valor"] = "outra_medida"
    elif campo == "filtros": cand["consulta"]["filtros"] = {"status_id": [9]}
    elif campo == "execucao": c.estado["visualizacao_execucao_id"] = "antiga"
    elif campo == "usuario": c.estado["user_id"] = 99
    elif campo == "sessao": c.runtime.context["session_id"] = "outra"
    elif campo == "turno": c.runtime.context["turno_id"] = "outro"
    elif campo == "ferramenta": cand["ferramenta"] = "consultar_visualizacao_os_criacao"
    elif campo == "duplicada": c.estado["consultas_visualizacao"].append(copy.deepcopy(cand))
    elif campo == "ausente": c.estado["consultas_visualizacao"] = []
    elif campo == "sem_dados": cand["resultado"].update(status="SEM_RESULTADO", dados=None)
    else: c.estado["visualizacao_status"] = "SEM_RESULTADO"
    resultado = asyncio.run(juiz.julgar_resposta(c.estado, c.runtime))
    assert resultado["veredito"] == "bloqueado" and resultado["erro"]
    assert resultado["visualizacao_aprovacao"] is None and resultado["visualizacao_aprovada"] is None
    c.julgar.assert_not_awaited()


def test_incompatibilidade_exige_nova_consulta_e_nao_revisao_textual(cenario):
    c = cenario
    c.julgar.return_value = avaliacao(incompatibilidade=0.95)
    resultado = asyncio.run(juiz.julgar_resposta(c.estado, c.runtime))
    assert resultado["veredito"] == "bloqueado"
    assert "não atende" in resultado["feedback_juiz"]
    assert resultado["visualizacao_candidata"] is None
    c.julgar.assert_awaited_once()


@pytest.mark.parametrize("erro", [RuntimeError("segredo-token-teste driver sql"), None])
def test_erro_ou_resposta_jev_incompleta_nao_libera_dados(cenario, caplog, erro):
    c = cenario
    if erro: c.julgar.side_effect = erro
    else: c.julgar.return_value["answers"].pop("visualizacao_incompativel")
    resultado = asyncio.run(juiz.julgar_resposta(c.estado, c.runtime))
    assert resultado["veredito"] == "bloqueado" and resultado["visualizacao_candidata"] is None
    assert "segredo-token-teste" not in json.dumps(resultado) + caplog.text


@pytest.mark.parametrize("campo", ["dados", "avisos", "status", "texto", "hash", "sem_aprovacao", "turno", "rota"])
def test_alteracao_apos_aprovacao_impede_envio(cenario, campo):
    c = cenario
    estado = julgar(c)
    if campo in {"dados", "avisos"}:
        for r in [estado["visualizacao_candidata"], *estado["consultas_visualizacao"]]:
            if campo == "dados": r["resultado"]["dados"]["pontos"][0]["valor"] = 999
            else: r["resultado"]["avisos"].append("Novo aviso")
    elif campo == "status": estado["visualizacao_status"] = "SUCESSO_PARCIAL"
    elif campo == "texto": estado["resposta_candidata"] = "Há 999 OS."
    elif campo == "hash": estado["visualizacao_aprovacao"]["conteudo_sha256"] = "0" * 64
    elif campo == "sem_aprovacao": estado["visualizacao_aprovacao"] = None
    elif campo == "turno": c.runtime.context["turno_id"] = "novo-turno"
    else: estado["intencao"] = "faq"
    resultado = nos.validar_saida(estado, c.runtime)
    assert resultado["visualizacao_aprovada"] is None and resultado["saida_bloqueada"]
    assert resultado["messages"][-1].content == resultado["resposta_final"]
    assert "999" not in resultado["resposta_final"]


@pytest.mark.parametrize("bloqueio", ["bloqueado", "erro", "vazio"])
def test_guardrail_recusa_sem_dados_aprovados(monkeypatch, cenario, bloqueio):
    c = cenario
    estado = julgar(c)
    def proteger(**kwargs):
        if bloqueio == "erro": raise RuntimeError("indisponível")
        return {"bloqueado": bloqueio == "bloqueado", "conteudo": "" if bloqueio == "vazio" else "Recusada"}
    monkeypatch.setattr(nos, "proteger_saida", proteger)
    resultado = nos.validar_saida(estado, c.runtime)
    assert resultado["visualizacao_aprovada"] is None and resultado["visualizacao_candidata"] is None


def test_redacao_de_pii_no_texto_preserva_dados(cenario):
    c = cenario
    c.estado["resposta_especialista"] += " Contato: contato@exemplo.com."
    resultado = nos.validar_saida(julgar(c), c.runtime)
    assert "[EMAIL OMITIDO]" in resultado["resposta_final"]
    assert resultado["visualizacao_aprovada"]["dados"]["pontos"][0]["valor"] == 2


def test_revisao_recebe_dados_preserva_captura_e_exige_novo_julgamento(monkeypatch, cenario):
    c = cenario
    c.julgar.return_value = avaliacao("revisar", sem_suporte=0.95)
    estado = julgar(c)
    assert estado["veredito"] == "revisar" and estado["visualizacao_aprovacao"] is None
    revisar = AsyncMock(return_value=juiz.RespostaRevisada(resposta="São 2 OS finalizadas."))
    modelos = import_module("app.agents.modelos")
    modelo = Mock(with_structured_output=Mock(return_value=SimpleNamespace(ainvoke=revisar)))
    monkeypatch.setattr(modelos, "llm_especialista", modelo)
    revisado = asyncio.run(juiz.revisar_resposta(estado, c.runtime))
    assert revisado["erro"] is None and revisado["veredito"] is None
    assert revisado["visualizacao_aprovacao"] is None
    entrada = json.loads(revisar.await_args.args[0][1].content)
    assert entrada["visualizacao"]["candidata"]["resultado"]["dados"]["pontos"][0]["valor"] == 2
    assert estado["visualizacao_candidata"] == c.estado["visualizacao_candidata"]
    pendente = {**estado, **revisado}
    assert nos.validar_saida(pendente, c.runtime)["visualizacao_aprovada"] is None
    c.julgar.return_value = avaliacao()
    segundo = asyncio.run(juiz.julgar_resposta(pendente, c.runtime))
    saida = nos.validar_saida({**pendente, **segundo}, c.runtime)
    assert saida["resposta_final"] == "São 2 OS finalizadas."
    assert saida["visualizacao_aprovada"] == c.estado["visualizacao_candidata"]["resultado"]
    assert c.banco.await_count == 1


@pytest.mark.parametrize("falha", ["extra", "vazia", "excecao"])
def test_falha_revisao_nao_preserva_aprovacao(monkeypatch, cenario, falha):
    c = cenario
    estado = julgar(c)
    dados = {"resposta": "Texto corrigido", "visualizacao": {"dados": [999]}} if falha == "extra" else {"resposta": " "}
    revisao = SimpleNamespace(model_dump=lambda: dados)
    revisar = AsyncMock(return_value=revisao, side_effect=RuntimeError("falha") if falha == "excecao" else None)
    monkeypatch.setattr(import_module("app.agents.modelos"), "llm_especialista",
                        SimpleNamespace(with_structured_output=lambda _: SimpleNamespace(ainvoke=revisar)))
    resultado = asyncio.run(juiz.revisar_resposta(estado, c.runtime))
    assert resultado["erro"] and resultado["visualizacao_aprovada"] is None
    assert resultado["visualizacao_candidata"] is None


@pytest.mark.parametrize("status", ["AGUARDANDO_INFORMACAO", "SEM_RESULTADO", "SEM_BASE_CALCULO", "TIMEOUT"])
def test_resposta_sem_candidata_nao_inventa_grafico(cenario, status):
    c = cenario
    c.estado.update(visualizacao_candidata=None, consultas_visualizacao=[], visualizacao_status=status)
    resultado = julgar(c)
    assert resultado["veredito"] == "aprovado" and resultado["visualizacao_aprovacao"] is None
    assert nos.validar_saida(resultado, c.runtime)["visualizacao_aprovada"] is None


@pytest.mark.parametrize("vereditos", [["aprovado"], ["revisar", "aprovado"], ["revisar", "revisar"]])
def test_grafo_compilado_julga_revisa_e_libera_sem_repetir_consulta(monkeypatch, cenario, vereditos):
    c = cenario
    c.banco.reset_mock()
    c.unidade.reset_mock()
    c.agente.ainvoke.reset_mock()
    c.julgar.side_effect = [avaliacao(v) for v in vereditos]
    async def supervisionar(_estado):
        return {"intencao": "visualizacao", "erro": None}
    async def emocao(_estado):
        return {"emocao": "neutro"}
    monkeypatch.setattr(fluxo, "supervisionar", supervisionar)
    monkeypatch.setattr(fluxo, "classificar_emocao", emocao)
    monkeypatch.setattr(nos, "proteger_entrada", lambda _: {"bloqueado": False})
    revisar = AsyncMock(return_value=juiz.RespostaRevisada(resposta="São 2 OS finalizadas."))
    monkeypatch.setattr(import_module("app.agents.modelos"), "llm_especialista",
                        SimpleNamespace(with_structured_output=lambda _: SimpleNamespace(ainvoke=revisar)))
    grafo = fluxo.construir_grafo()
    inicial = criar_estado_inicial(c.estado["messages"], c.runtime.context["usuario"])
    resultado = asyncio.run(grafo.ainvoke(inicial, context=c.runtime.context,
                                        config={"configurable": {"thread_id": "10:sessao-1"}}))
    assert c.banco.await_count == c.unidade.await_count == c.agente.ainvoke.await_count == 1
    assert c.julgar.await_count == len(vereditos)
    if vereditos[-1] == "aprovado":
        assert resultado["visualizacao_aprovada"]["dados"]["pontos"][0]["valor"] == 2
    else:
        assert resultado["visualizacao_aprovada"] is None and resultado["visualizacao_candidata"] is None
    assert revisar.await_count == (1 if len(vereditos) == 2 else 0)


def test_sucesso_parcial_preserva_avisos_no_julgamento_e_na_saida(cenario):
    c = cenario
    for r in [c.estado["visualizacao_candidata"], *c.estado["consultas_visualizacao"]]:
        r["resultado"].update(status="SUCESSO_PARCIAL", avisos=["Cobertura parcial informada pela ferramenta."])
    c.estado["visualizacao_status"] = "SUCESSO_PARCIAL"
    estado = julgar(c)
    contexto = c.julgar.await_args.args[0]
    assert contexto["visualizacao"]["candidata"]["resultado"]["avisos"]
    saida = nos.validar_saida(estado, c.runtime)
    assert saida["visualizacao_aprovada"]["status"] == "SUCESSO_PARCIAL"
    assert saida["visualizacao_aprovada"]["avisos"] == ["Cobertura parcial informada pela ferramenta."]


@pytest.mark.parametrize("etapa", ["julgamento", "revisao", "protecao"])
def test_alteracao_durante_etapa_e_detectada(monkeypatch, cenario, etapa):
    c = cenario
    estado = c.estado if etapa == "julgamento" else julgar(c)
    def adulterar():
        for r in [estado["visualizacao_candidata"], *estado["consultas_visualizacao"]]:
            r["resultado"]["dados"]["pontos"][0]["valor"] = 999
    if etapa == "julgamento":
        async def avaliar(*args, **kwargs):
            adulterar()
            return avaliacao()
        c.julgar.side_effect = avaliar
        resultado = asyncio.run(juiz.julgar_resposta(estado, c.runtime))
    elif etapa == "revisao":
        async def revisar(*args, **kwargs):
            adulterar()
            return juiz.RespostaRevisada(resposta="Texto revisado.")
        monkeypatch.setattr(import_module("app.agents.modelos"), "llm_especialista",
                            SimpleNamespace(with_structured_output=lambda _: SimpleNamespace(ainvoke=revisar)))
        resultado = asyncio.run(juiz.revisar_resposta(estado, c.runtime))
    else:
        def proteger(**kwargs):
            adulterar()
            return {"conteudo": kwargs["resposta"], "bloqueado": False}
        monkeypatch.setattr(nos, "proteger_saida", proteger)
        resultado = nos.validar_saida(estado, c.runtime)
    assert resultado["erro"] and resultado["visualizacao_aprovada"] is None
    assert resultado["visualizacao_candidata"] is None


def test_dados_sem_contexto_autenticado_nao_sao_avaliados(cenario):
    c = cenario
    resultado = asyncio.run(juiz.julgar_resposta(c.estado))
    assert resultado["veredito"] == "bloqueado" and resultado["visualizacao_aprovada"] is None
    c.julgar.assert_not_awaited()


def test_registro_model_construct_tambem_e_revalidado(cenario):
    from app.schemas.visualizacao import ConsultaVisualizacaoCapturada
    c = cenario
    registro = ConsultaVisualizacaoCapturada.model_validate(c.estado["visualizacao_candidata"])
    adulterado = registro.model_copy(update={"chamada_id": 123})
    c.estado["visualizacao_candidata"] = adulterado
    c.estado["consultas_visualizacao"] = [adulterado]
    resultado = asyncio.run(juiz.julgar_resposta(c.estado, c.runtime))
    assert resultado["veredito"] == "bloqueado"
    c.julgar.assert_not_awaited()
