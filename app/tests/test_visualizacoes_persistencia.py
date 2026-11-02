"""Contrato público, gravação atômica e histórico com bancos e modelos simulados."""

import asyncio
import copy
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from importlib import import_module
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from bson import BSON
from fastapi import HTTPException
from fastapi.testclient import TestClient
from langchain.tools import ToolRuntime
from langchain_core.messages import HumanMessage
from pymongo.errors import AutoReconnect

from app.agents.agentsResult import VisualizacaoResultado
from app.api.dependencies.auth import obter_usuario_atual
from app.graph import executor, nos
from app.main import app
from app.schemas import ConversaSaida, UsuarioContexto
from app.services import chat
from app.services.indicadores.gerais import databricks
from app.services.visualizacoes import ANALISES, publicacao
from app.tools.metricas_kpis import contexto as contexto_indicadores
from app.tools.visualizacoes import FERRAMENTAS_VISUALIZACOES

salvar = import_module("app.memory.persistencia.salvar_mensagem")
historico = import_module("app.services.sessoes.historico")
juiz = import_module("app.agents.juiz")


@pytest.fixture
def origem(monkeypatch, request):
    monkeypatch.setenv("LANGSMITH_TRACING", "false")
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "false")
    usuario = UsuarioContexto(access_token="token-secreto", usuario_id=10, nome_completo="Gestor",
                             email="teste@example.com", tipo_acesso="gestor", cnpj_endereco="12345678000195")
    ctx = {"usuario": usuario, "session_id": "sessao", "turno_id": "turno"}
    banco = AsyncMock(return_value=[{
        "status_id": None, "status_os": None, "valor": "2", "qtd_registros": "2",
        "instante_snapshot": "2026-10-30T12:00:00+00:00",
    }])
    monkeypatch.setattr(databricks, "executar_consulta", banco)
    monkeypatch.setattr(contexto_indicadores, "obter_unidade_id", AsyncMock(return_value=7))
    analise_id = getattr(request, "param", "VIS-03")
    if analise_id == "VIS-05":
        banco.return_value = [{"tecnico_id": "21", "tecnico_nome": "Técnico João", "valor": "2", "qtd_registros": "2"}]
    analise = ANALISES[analise_id]
    tool = next(t for t in FERRAMENTAS_VISUALIZACOES if t.name == f"consultar_visualizacao_{analise.fonte.id}")
    async def agente(_entrada, *, context):
        runtime = ToolRuntime(state={}, context=context, config={}, stream_writer=lambda _: None,
                              tool_call_id="chamada", store=None)
        argumentos = {"analise_id": analise_id, "runtime": runtime}
        if analise.fonte.campo_periodo:
            argumentos["periodo"] = {"inicio": "2026-10-01", "fim": "2026-10-04"}
        dados = await tool.ainvoke(argumentos)
        return {"structured_response": VisualizacaoResultado(
            agente="visualizacao", resposta="Há 2 OS no recorte.", status="SUCESSO",
            visualizacao={"analise_id": analise_id, "consulta_id": dados["metadados"]["consulta_id"]},
        )}
    monkeypatch.setattr(nos, "visualizacoes_gestor", SimpleNamespace(ainvoke=AsyncMock(side_effect=agente)))
    monkeypatch.setattr(juiz, "consultar_jev", AsyncMock(return_value={"model": "teste", "answers": {
        "veredito": {"type": "choice", "choice": "aprovado", "confidence": 0.95},
        "motivo": {"type": "choice", "choice": "nenhum", "confidence": 0.95},
        **{k: {"type": "noul", "noul": 0.05} for k in (
            "afirmacao_sem_suporte", "correcao_textual", "risco_grave", "visualizacao_incompativel",
        )},
    }}))
    async def executar(ctx_atual):
        runtime = SimpleNamespace(context=ctx_atual)
        estado = {"messages": [HumanMessage(content="Mostre as OS por status.")],
                  "perfil": "gestor", "user_id": 10, "intencao": "visualizacao", "mapa_pii": {}}
        estado.update(await nos.executar_visualizacao(estado, runtime))
        estado.update(await juiz.julgar_resposta(estado, runtime))
        estado.update(nos.validar_saida(estado, runtime))
        return estado
    estado = asyncio.run(executar(ctx))
    grafico = publicacao.publicar_visualizacao(estado, ctx).model_dump(mode="json")
    return SimpleNamespace(ctx=ctx, usuario=usuario, estado=estado, grafico=grafico,
                           banco=banco, executar=executar)


def avaliar(expressao, doc):
    """Semântica dos operadores Mongo usados no filtro, sobre BSON real."""
    if expressao == "$$ROOT": return doc
    if isinstance(expressao, str) and expressao.startswith("$"): return doc.get(expressao[1:])
    if isinstance(expressao, list): return [avaliar(v, doc) for v in expressao]
    if not isinstance(expressao, dict): return expressao
    if "$literal" in expressao: return copy.deepcopy(expressao["$literal"])
    if "$cond" in expressao:
        cond, sim, nao = expressao["$cond"]
        return avaliar(sim if avaliar(cond, doc) else nao, doc)
    if "$lte" in expressao:
        a, b = avaliar(expressao["$lte"], doc)
        return a <= b
    if "$bsonSize" in expressao: return len(BSON.encode(avaliar(expressao["$bsonSize"], doc)))
    if "$ifNull" in expressao:
        a, b = expressao["$ifNull"]
        valor = avaliar(a, doc)
        return avaliar(b, doc) if valor is None else valor
    if "$concatArrays" in expressao: return sum(avaliar(expressao["$concatArrays"], doc), [])
    if "$mergeObjects" in expressao:
        resultado = {}
        for item in expressao["$mergeObjects"]: resultado.update(avaliar(item, doc))
        return resultado
    return {k: avaliar(v, doc) for k, v in expressao.items()}


class Colecao:
    def __init__(self):
        instante = datetime(2026, 10, 31, tzinfo=timezone.utc)
        self.doc = {"_id": "documento", "session_id": "sessao", "user_id": 10, "esta_ativo": True,
                    "iniciada_em": instante, "atualizada_em": instante, "titulo": "", "resumo": "",
                    "mensagens": [{"role": "human", "content": "Pedido"}]}
        self.lock = asyncio.Lock()
        self.filtros = []

    def corresponde(self, filtro):
        for k, v in filtro.items():
            if k == "$expr":
                if not avaliar(v, self.doc): return False
            elif k == "mensagens.turno_id":
                if any(m.get("turno_id") == v["$ne"] for m in self.doc["mensagens"]): return False
            elif self.doc.get(k) != v: return False
        return True

    async def update_one(self, filtro, alteracao):
        async with self.lock:
            self.filtros.append(copy.deepcopy(filtro))
            if not self.corresponde(filtro): return SimpleNamespace(matched_count=0)
            self.doc["mensagens"].append(copy.deepcopy(alteracao["$push"]["mensagens"]))
            self.doc.update(alteracao["$set"])
            return SimpleNamespace(matched_count=1)

    async def find_one(self, filtro, projecao=None, **kwargs):
        if not self.corresponde(filtro): return None
        if projecao and isinstance(projecao.get("mensagens"), dict):
            alvo = projecao["mensagens"]["$elemMatch"]
            return {"_id": self.doc["_id"], "mensagens": [copy.deepcopy(m) for m in self.doc["mensagens"]
                    if all(m.get(k) == v for k, v in alvo.items())][:1]}
        return copy.deepcopy(self.doc)


@pytest.fixture
def mongo(monkeypatch):
    colecao = Colecao()
    @asynccontextmanager
    async def abrir():
        yield {salvar.MONGO_BANCO_DADOS: {salvar.MONGO_COLECAO_SESSOES: colecao}}
    monkeypatch.setattr(salvar, "abrir_cliente_mongo", abrir)
    monkeypatch.setattr(historico, "abrir_cliente_mongo", abrir)
    monkeypatch.setattr(salvar, "obter_documento_sessao_id", AsyncMock(return_value="documento"))
    return colecao


def gravar(origem, turno="turno"):
    return salvar.salvar_mensagem("sessao", "assistant", "Há 2 OS no recorte.", 10,
                                  turno_id=turno, visualizacao=origem.grafico)


def test_mesmo_payload_publico_persistido_e_recuperado(origem, mongo, capsys):
    asyncio.run(gravar(origem))
    conversa = asyncio.run(historico.buscar_conversa("sessao", 10, incluir_visualizacoes=True))
    assert conversa["mensagens"][-1]["visualizacao"] == origem.grafico == mongo.doc["mensagens"][-1]["visualizacao"]
    assert conversa["mensagens"][-1]["mensagem"] == "Há 2 OS no recorte."
    assert origem.grafico["dados"]["pontos"][0]["grupo"] == {"status_id": None, "status_os": None}
    assert origem.grafico["metadados"]["unidade_id"] == 7
    assert not {"fonte", "campo_valor", "consulta_id", "filtros_aplicados"} & origem.grafico["metadados"].keys()
    assert not {"usuario_id", "sessao_id", "turno_id", "execucao_id"} & origem.grafico.keys()
    assert origem.banco.await_count == 1
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize("campo", ["valor", "texto", "sem_aprovacao"])
def test_publicacao_rejeita_alteracao_ou_falta_de_aprovacao(origem, campo):
    estado = copy.deepcopy(origem.estado)
    if campo == "valor": estado["visualizacao_aprovada"]["dados"]["pontos"][0]["valor"] = 999
    elif campo == "texto": estado["resposta_final"] = "Há 999 OS."
    else: estado["visualizacao_aprovacao"] = None
    with pytest.raises(ValueError): publicacao.publicar_visualizacao(estado, origem.ctx)


def test_limite_utf8_exato_sem_truncar(origem):
    dados = copy.deepcopy(origem.grafico)
    dados["titulo"] = "a"
    base = len(publicacao.VisualizacaoPublica.model_validate(dados).model_dump_json().encode("utf-8"))
    dados["titulo"] = "a" * (publicacao.MAXIMO_BYTES_VISUALIZACAO - base + 1)
    assert len(publicacao.validar_visualizacao_publica(dados).model_dump_json().encode("utf-8")) == 256 * 1024
    dados["titulo"] += "é"
    with pytest.raises(publicacao.LimiteVisualizacaoExcedido): publicacao.validar_visualizacao_publica(dados)


@pytest.mark.parametrize("papel,turno", [("human", "turno"), ("assistant", None)])
def test_nao_grava_grafico_em_papel_ou_turno_invalidos(origem, mongo, papel, turno):
    with pytest.raises(ValueError):
        asyncio.run(salvar.salvar_mensagem("sessao", papel, "Texto", 10, turno_id=turno, visualizacao=origem.grafico))
    assert len(mongo.doc["mensagens"]) == 1


def test_repeticao_identica_nao_duplica_e_conflito_nao_substitui(origem, mongo, monkeypatch):
    asyncio.run(gravar(origem))
    timestamp = mongo.doc["mensagens"][-1]["timestamp"]
    monkeypatch.setattr(salvar, "agora", lambda: timestamp + timedelta(seconds=30))
    asyncio.run(gravar(origem))
    assert len(mongo.doc["mensagens"]) == 2
    assert mongo.doc["mensagens"][-1]["timestamp"] == timestamp
    with pytest.raises(HTTPException) as erro:
        asyncio.run(salvar.salvar_mensagem("sessao", "assistant", "Outro texto", 10,
                                          turno_id="turno", visualizacao=origem.grafico))
    assert erro.value.status_code == 409 and len(mongo.doc["mensagens"]) == 2


@pytest.mark.parametrize("campo,valor", [("user_id", 20), ("session_id", "outra"), ("esta_ativo", False)])
def test_gravacao_filtra_dono_sessao_e_conversa_ativa(origem, mongo, campo, valor):
    mongo.doc[campo] = valor
    with pytest.raises(HTTPException) as erro: asyncio.run(gravar(origem))
    assert erro.value.status_code == 404 and len(mongo.doc["mensagens"]) == 1


def test_quota_atomica_em_gravacoes_concorrentes(monkeypatch, origem, mongo):
    # Cada resposta cabe isoladamente; as duas juntas ultrapassam o limite BSON.
    instante = salvar.agora()
    mensagem = {"role": "assistant", "content": "Há 2 OS no recorte.", "emocao": "NEUTRO", "confirmacao": "nao",
                "turno_id": "turno-a", "visualizacao": origem.grafico}
    proximo = {**mongo.doc, "mensagens": [*mongo.doc["mensagens"], mensagem], "atualizada_em": instante}
    limite = len(BSON.encode(proximo)) + 30
    monkeypatch.setattr(salvar, "MAXIMO_BYTES_CONVERSA_COM_VISUALIZACAO", limite)
    async def simultaneas():
        return await asyncio.gather(gravar(origem, "turno-a"), gravar(origem, "turno-b"), return_exceptions=True)
    resultados = asyncio.run(simultaneas())
    assert sum(r is None for r in resultados) == 1
    assert sum(isinstance(r, HTTPException) and r.status_code == 413 for r in resultados) == 1
    assert len(mongo.doc["mensagens"]) == 2 and len(BSON.encode(mongo.doc)) <= limite
    assert mongo.doc["mensagens"][0] == {"role": "human", "content": "Pedido"}


def test_dolar_em_rotulo_permanece_literal(origem, mongo):
    origem.grafico["dados"]["pontos"][0]["grupo"]["status_os"] = "$status_os"
    asyncio.run(gravar(origem))
    assert mongo.doc["mensagens"][-1]["visualizacao"]["dados"]["pontos"][0]["grupo"]["status_os"] == "$status_os"


def test_falha_mongo_nao_confirma_gravacao(origem, mongo, monkeypatch):
    monkeypatch.setattr(mongo, "update_one", AsyncMock(side_effect=AutoReconnect("token-secreto servidor")))
    with pytest.raises(HTTPException) as erro: asyncio.run(gravar(origem))
    assert erro.value.status_code == 503 and "token-secreto" not in erro.value.detail


def test_historico_antigo_e_perfil_sem_exposicao(origem, mongo):
    asyncio.run(gravar(origem))
    privado = asyncio.run(historico.buscar_conversa("sessao", 10))
    assert all("visualizacao" not in m for m in privado["mensagens"])
    assert asyncio.run(historico.buscar_conversa("sessao", 20, incluir_visualizacoes=True)) is None
    legado = historico._formatar_mensagens([{"role": "assistant", "content": "Mensagem antiga"}], incluir_visualizacoes=True)
    assert "visualizacao" not in legado[0] and legado[0]["mensagem"] == "Mensagem antiga"


@pytest.mark.parametrize("rota", ["chat", "historico"])
def test_api_preserva_nulos_e_mesmo_payload(monkeypatch, origem, mongo, rota):
    app.dependency_overrides[obter_usuario_atual] = lambda: origem.usuario
    if rota == "chat":
        monkeypatch.setattr(chat, "sessao_acessivel", AsyncMock(return_value=True))
        monkeypatch.setattr(chat, "executar_grafo", AsyncMock(return_value={
            "resposta_final": "Há 2 OS no recorte.", "intencao": "visualizacao", "visualizacao_publica": origem.grafico,
        }))
    else: asyncio.run(gravar(origem))
    try:
        cliente = TestClient(app)
        r = cliente.post("/api/v1/chat" if rota == "chat" else "/api/v1/sessoes/conversa",
                         json={"mensagem": "Pedido", "plataforma": "web", "thread_id": "sessao"} if rota == "chat" else {"session_id": "sessao"})
    finally: app.dependency_overrides.clear()
    assert r.status_code == 200, r.text
    dado = r.json()["visualizacao"] if rota == "chat" else r.json()["conversa"]["mensagens"][-1]["visualizacao"]
    assert dado == origem.grafico


@pytest.mark.parametrize("perfil", ["tecnico", "solicitante"])
def test_api_historico_so_expoe_grafico_ao_gestor_dono(monkeypatch, origem, mongo, perfil):
    asyncio.run(gravar(origem))
    usuario = origem.usuario.model_copy(update={"tipo_acesso": perfil})
    app.dependency_overrides[obter_usuario_atual] = lambda: usuario
    try: r = TestClient(app).post("/api/v1/sessoes/conversa", json={"session_id": "sessao"})
    finally: app.dependency_overrides.clear()
    assert r.status_code == 200
    assert all("visualizacao" not in m for m in r.json()["conversa"]["mensagens"])


@pytest.mark.parametrize("falha", [False, True])
def test_executor_persiste_antes_de_disponibilizar_ao_chat(monkeypatch, origem, falha):
    async def invocar(_estado, *, context, **kwargs): return await origem.executar(context)
    monkeypatch.setattr(executor, "grafo", SimpleNamespace(get_state=lambda _: SimpleNamespace(values={"messages": []}),
                                                         ainvoke=AsyncMock(side_effect=invocar)))
    for nome, valor in [("obter_rascunho_solicitacao", None), ("obter_acao", None), ("obter_analise_compra", None),
                        ("obter_quantidade_anexos_pendentes", 0)]:
        monkeypatch.setattr(executor, nome, AsyncMock(return_value=valor))
    mensagens = []
    async def persistir(*args, **kwargs):
        mensagens.append((args, copy.deepcopy(kwargs)))
        if args[1] == "assistant" and falha: raise HTTPException(status_code=503, detail="Falha de gravação")
    monkeypatch.setattr(executor, "salvar_mensagem", persistir)
    if falha:
        with pytest.raises(HTTPException): asyncio.run(executor.executar_grafo("Pedido", origem.usuario, "sessao"))
    else:
        resultado = asyncio.run(executor.executar_grafo("Pedido", origem.usuario, "sessao"))
        assert resultado["visualizacao_publica"] == mensagens[-1][1]["visualizacao"]
    assert [m[0][1] for m in mensagens] == ["human", "assistant"]


def test_contrato_textual_continua_sem_campo_visualizacao():
    assert "visualizacao" not in ConversaSaida(thread_id="sessao", intencao="faq", resposta="Texto").model_dump(mode="json")


@pytest.mark.parametrize("recusa", [False, True])
def test_api_com_executor_e_persistencia_reais_no_mongo_simulado(monkeypatch, origem, mongo, recusa):
    async def invocar(_estado, *, context, **kwargs): return await origem.executar(context)
    monkeypatch.setattr(executor, "grafo", SimpleNamespace(get_state=lambda _: SimpleNamespace(values={"messages": []}),
                                                         ainvoke=AsyncMock(side_effect=invocar)))
    monkeypatch.setattr(executor, "salvar_mensagem", salvar.salvar_mensagem)
    monkeypatch.setattr(chat, "executar_grafo", executor.executar_grafo)
    monkeypatch.setattr(chat, "sessao_acessivel", AsyncMock(return_value=True))
    for nome, valor in [("obter_rascunho_solicitacao", None), ("obter_acao", None), ("obter_analise_compra", None),
                        ("obter_quantidade_anexos_pendentes", 0)]:
        monkeypatch.setattr(executor, nome, AsyncMock(return_value=valor))
    if recusa: monkeypatch.setattr(salvar, "MAXIMO_BYTES_CONVERSA_COM_VISUALIZACAO", 1)
    origem.banco.reset_mock()
    app.dependency_overrides[obter_usuario_atual] = lambda: origem.usuario
    try:
        cliente = TestClient(app)
        resposta = cliente.post("/api/v1/chat", json={"mensagem": "Novo pedido", "plataforma": "web", "thread_id": "sessao"})
        recuperado = cliente.post("/api/v1/sessoes/conversa", json={"session_id": "sessao"})
    finally: app.dependency_overrides.clear()
    assert origem.banco.await_count == 1
    if recusa:
        assert resposta.status_code == 413
        assert isinstance(mongo.doc["mensagens"][-1]["timestamp"], datetime)
        assert mongo.doc["mensagens"][-1] == {
            "role": "human", "content": "Novo pedido", "timestamp": mongo.doc["mensagens"][-1]["timestamp"],
        }
        assert all("visualizacao" not in m for m in recuperado.json()["conversa"]["mensagens"])
    else:
        assert resposta.status_code == 200, resposta.text
        assert resposta.json()["visualizacao"] == mongo.doc["mensagens"][-1]["visualizacao"]
        assert resposta.json()["visualizacao"] == recuperado.json()["conversa"]["mensagens"][-1]["visualizacao"]


@pytest.mark.parametrize("alteracao", ["versao", "nan", "extra"])
def test_contrato_publico_recusa_conteudo_invalido(origem, alteracao):
    dados = copy.deepcopy(origem.grafico)
    if alteracao == "versao": dados["versao_contrato"] = "2.0"
    elif alteracao == "nan": dados["dados"]["pontos"][0]["valor"] = float("nan")
    else: dados["configuracao_recharts"] = {"script": "conteudo"}
    with pytest.raises(ValueError): publicacao.validar_visualizacao_publica(dados)


def test_historico_incompativel_nao_recalcula_nem_vaza_dados(origem, mongo):
    asyncio.run(gravar(origem))
    mongo.doc["mensagens"][-1]["visualizacao"]["versao_contrato"] = "2.0"
    with pytest.raises(historico.ErroConsultaHistorico) as erro:
        asyncio.run(historico.buscar_conversa("sessao", 10, incluir_visualizacoes=True))
    assert erro.value.status_code == 500
    assert origem.banco.await_count == 1


@pytest.mark.parametrize("origem", ["VIS-05"], indirect=True)
def test_nome_e_id_do_tecnico_preservados(origem, mongo):
    asyncio.run(gravar(origem))
    conversa = asyncio.run(historico.buscar_conversa("sessao", 10, incluir_visualizacoes=True))
    grupo = conversa["mensagens"][-1]["visualizacao"]["dados"]["pontos"][0]["grupo"]
    assert grupo == {"tecnico_id": 21, "tecnico_nome": "Técnico João"}
