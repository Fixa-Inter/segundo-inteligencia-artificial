"""Contrato e regras do cadastro de eventos, sem chamadas a serviços externos."""

import asyncio
import json
from contextlib import asynccontextmanager
from copy import deepcopy
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import httpx
import pytest
from pydantic import ValidationError

from app.agents.agentsResult import SolicitacaoOcorrenciaResultado
from app.core.confirmacoes import classificar_manifestacao
from app.core.propostas import avaliar_confirmacao, metadados_proposta
from app.graph import continuacoes
from app.schemas import ConversaSaida, UsuarioContexto
from app.services.operacoes import dados_cadastro
from app.services.operacoes import aprovacao_operacoes
from app.tools.toolsRequest import CriarEventoEntrada

ferramentas = import_module("app.tools.eventos.criarEvento")
busca = import_module("app.tools.eventos.buscarOpcoesEvento")
servico = import_module("app.services.eventos.criarEvento")


def dados_evento(**campos):
    return {
        "local_unidade_id": 2, "titulo": "Treinamento de manutenção",
        "descricao": "Treinamento da equipe no auditório",
        "data_hora_inicio": "2020-01-10T09:00:00",
        "data_hora_fim": "2020-01-10T11:00:00", **campos,
    }


@pytest.fixture
def contexto_evento():
    return {"usuario": UsuarioContexto.model_construct(
        usuario_id=7, tipo_acesso="gestor", access_token="token-teste",
    ), "session_id": "sessao", "turno_id": "confirmacao",
        "mensagem_atual": "Pode criar o evento", "intencao_atual": "evento",
        "imagens": [], "operacoes_pendentes": [], "resultados_operacoes": []}


@pytest.fixture
def proposta_evento():
    dados = CriarEventoEntrada(**dados_evento()).model_dump(mode="json")
    return {"id": "proposta", "versao": 1, "tipo": "evento", "turno_id": "coleta",
            "turno_apresentacao": "apresentacao", "versao_apresentada": 1,
            "dados_apresentados": dados.copy(), "dados": dados, "dados_confirmados": {},
            "status_fluxo": "aguardando_confirmacao", "imagens": [],
            "rotulos": {"local_unidade_id": "Auditório"}}


def test_horarios_sem_fuso_sao_normalizados_e_passado_e_permitido():
    evento = CriarEventoEntrada(**dados_evento())
    assert evento.data_hora_inicio == datetime(2020, 1, 10, 12, tzinfo=timezone.utc)
    assert evento.model_dump(mode="json")["data_hora_fim"] == "2020-01-10T14:00:00Z"
    assert evento.descricao_local == evento.observacao == "Não foi especificado"


def test_horarios_com_fuso_preservam_instante_e_comparam_em_utc():
    evento = CriarEventoEntrada(**dados_evento(
        data_hora_inicio="2020-01-10T09:00:00-05:00", data_hora_fim="2020-01-10T15:00:00Z",
    ))
    assert evento.model_dump(mode="json")["data_hora_inicio"] == "2020-01-10T14:00:00Z"


@pytest.mark.parametrize("campos", [
    {"data_hora_fim": "2020-01-10T09:00:00"},
    {"data_hora_fim": "2020-01-10T08:00:00"},
    {"data_hora_inicio": "2020-01-10T12:00:00Z", "data_hora_fim": "2020-01-10T09:00:00-03:00"},
    {"data_hora_inicio": "2020-01-10"}, {"data_hora_fim": None},
    {"data_hora_inicio": 1578657600}, {"data_hora_inicio": "amanhã às nove"},
    {"local_unidade_id": 0}, {"local_unidade_id": True}, {"local_unidade_id": "2"},
    {"titulo": "palavra " * 11}, {"titulo": "x" * 101}, {"descricao": "x" * 256},
    {"observacao": "x" * 256}, {"descricao_local": "x" * 256},
    {"usuario_id": 99}, {"access_token": "inventado"},
])
def test_dados_invalidos_sao_recusados(campos):
    with pytest.raises(ValidationError):
        CriarEventoEntrada(**dados_evento(**campos))


@pytest.mark.parametrize("campo", ["local_unidade_id", "titulo", "descricao", "data_hora_inicio", "data_hora_fim"])
def test_campos_obrigatorios(campo):
    dados = dados_evento()
    dados.pop(campo)
    with pytest.raises(ValidationError):
        CriarEventoEntrada(**dados)


def simular_http(monkeypatch, status=200, corpo=None):
    resposta = httpx.Response(status, json={"id": 15, "titulo": "Treinamento"} if corpo is None else corpo)
    post = AsyncMock(return_value=resposta)
    cliente = AsyncMock()
    cliente.__aenter__.return_value = SimpleNamespace(post=post)
    monkeypatch.setattr(servico.httpx, "AsyncClient", Mock(return_value=cliente))
    monkeypatch.setattr(servico, "FIXA_URL_BASE_API", "https://example.com/")
    return post


def test_payload_bearer_identidade_e_datas_seguem_contrato(monkeypatch):
    post = simular_http(monkeypatch)
    resultado = asyncio.run(servico.adicionar_evento(
        CriarEventoEntrada(**dados_evento()), "token-teste", usuario_id=7,
    ))
    spec = json.loads((Path(__file__).resolve().parents[2] / "docs/api/swagger.json").read_text(encoding="utf-8"))
    corpo = post.await_args.kwargs["json"]
    assert set(corpo) == set(spec["components"]["schemas"]["EventoCadastrarInputDTO"]["properties"])
    assert corpo["usuarioId"] == 7 and corpo["localUnidadeId"] == 2
    assert corpo["dataHoraInicio"] == "2020-01-10T12:00:00Z"
    assert corpo["dataHoraFim"] == "2020-01-10T14:00:00Z"
    assert corpo["descricaoLocal"] == corpo["observacao"] == "Não foi especificado"
    assert post.await_args.args == ("https://example.com/api/v1/eventos",)
    assert post.await_args.kwargs["headers"] == {"Authorization": "Bearer token-teste"}
    assert resultado["status"] == "SUCESSO" and resultado["evento_id"] == 15
    post.assert_awaited_once()


@pytest.mark.parametrize("status,corpo,esperado", [
    (201, {"id": 3, "titulo": "Evento"}, "SUCESSO"), (204, {}, "SUCESSO"),
    (202, {}, "RESULTADO_INDETERMINADO"), (500, {}, "RESULTADO_INDETERMINADO"),
    (200, {}, "RESULTADO_INDETERMINADO"), (200, [], "RESULTADO_INDETERMINADO"),
    (400, {"erro": "token-teste"}, "ERRO_API"), (401, {}, "ERRO_API"), (403, {}, "ERRO_API"),
])
def test_interpretacao_http_sem_repeticao(monkeypatch, status, corpo, esperado):
    post = simular_http(monkeypatch, status, corpo)
    resultado = asyncio.run(servico.adicionar_evento(CriarEventoEntrada(**dados_evento()), "token-teste", usuario_id=7))
    assert resultado["status"] == esperado
    assert "token-teste" not in json.dumps(resultado)
    post.assert_awaited_once()


@pytest.mark.parametrize("falha", ["timeout", "json"])
def test_timeout_ou_resposta_invalida_nao_repetem_post(monkeypatch, falha):
    post = simular_http(monkeypatch)
    if falha == "timeout":
        post.side_effect = httpx.ReadTimeout("Resposta perdida")
    else:
        post.return_value = httpx.Response(200, text="Resposta sem JSON")
    resultado = asyncio.run(servico.adicionar_evento(CriarEventoEntrada(**dados_evento()), "token-teste", usuario_id=7))
    assert resultado["status"] == "RESULTADO_INDETERMINADO"
    post.assert_awaited_once()


@pytest.fixture
def local_evento(monkeypatch):
    @asynccontextmanager
    async def qdrant():
        yield "qdrant"
    unidade = AsyncMock(return_value=1)
    validar = AsyncMock(return_value="Auditório")
    for modulo in (ferramentas, busca):
        monkeypatch.setattr(modulo, "obter_unidade_id", unidade)
        monkeypatch.setattr(modulo, "abrir_cliente_qdrant", qdrant)
    monkeypatch.setattr(ferramentas, "validar_selecao", validar)
    return validar


@pytest.mark.parametrize("perfil", ["gestor", "administrador"])
def test_busca_filtra_unidade_autenticada(monkeypatch, contexto_evento, local_evento, perfil):
    contexto_evento["usuario"].tipo_acesso = perfil
    consultar = AsyncMock(return_value={2: "Auditório"})
    monkeypatch.setattr(busca, "buscar_local_endereco", consultar)
    resultado = asyncio.run(busca.buscar_opcoes_evento.coroutine("auditório", SimpleNamespace(context=contexto_evento)))
    assert resultado == {"local_unidade": {"2": "Auditório"}}
    consultar.assert_awaited_once_with("auditório", 1, "qdrant")


def test_rascunho_contem_utc_e_rotulos_locais_sem_identidade(monkeypatch, contexto_evento, local_evento):
    async def persistir(sessao, usuario, dados, **kwargs):
        return {"id": "proposta", "versao": 1, "tipo": "evento", "dados": dados,
                "rotulos": kwargs["rotulos"]}
    salvar = AsyncMock(side_effect=persistir)
    monkeypatch.setattr(ferramentas, "salvar_rascunho_solicitacao", salvar)
    resultado = asyncio.run(ferramentas.salvar_rascunho_evento.coroutine(
        **dados_evento(), runtime=SimpleNamespace(context=contexto_evento),
    ))
    assert resultado["status"] == "RASCUNHO_SALVO"
    assert salvar.await_args.kwargs["tipo"] == "evento"
    assert resultado["dados_salvos"]["data_hora_inicio"] == "2020-01-10T12:00:00Z"
    resumo = resultado["proposta"]["resumo_confirmacao"]
    assert "Local: Auditório" in resumo and "10/01/2020 às 09:00:00" in resumo
    assert "token-teste" not in resumo and "usuario_id" not in resumo
    local_evento.assert_awaited_once_with(ferramentas.QDRANT_COLECAO_LOCAL, 2, 1, "qdrant")


@pytest.mark.parametrize("perfil", ["tecnico", "solicitante"])
def test_tools_negam_perfis_nao_autorizados(monkeypatch, contexto_evento, perfil):
    contexto_evento["usuario"].tipo_acesso = perfil
    consultar = AsyncMock()
    salvar = AsyncMock()
    carregar = AsyncMock()
    monkeypatch.setattr(busca, "obter_unidade_id", consultar)
    monkeypatch.setattr(ferramentas, "salvar_rascunho_solicitacao", salvar)
    monkeypatch.setattr(ferramentas, "obter_rascunho_solicitacao", carregar)
    runtime = SimpleNamespace(context=contexto_evento)
    for resultado in (
        asyncio.run(busca.buscar_opcoes_evento.coroutine("auditório", runtime)),
        asyncio.run(ferramentas.salvar_rascunho_evento.coroutine(**dados_evento(), runtime=runtime)),
        asyncio.run(ferramentas.criar_evento.coroutine(runtime)),
        asyncio.run(ferramentas.processar_evento(runtime, operacao_aprovada={})),
    ):
        assert resultado["status"] == "ACESSO_NEGADO"
    consultar.assert_not_awaited()
    salvar.assert_not_awaited()
    carregar.assert_not_awaited()


@pytest.mark.parametrize("alteracao", [
    {"turno_id": "confirmacao"}, {"turno_apresentacao": None}, {"versao": 2},
    {"dados_apresentados": {}}, {"pausado": True}, {"status_fluxo": "coletando_dados"},
])
def test_proposta_nao_apresentada_ou_modificada_nao_prepara_envio(
    monkeypatch, contexto_evento, proposta_evento, alteracao,
):
    proposta_evento.update(alteracao)
    monkeypatch.setattr(ferramentas, "obter_rascunho_solicitacao", AsyncMock(return_value=proposta_evento))
    preparar = AsyncMock()
    enviar = AsyncMock()
    monkeypatch.setattr(ferramentas, "preparar_operacao", preparar)
    monkeypatch.setattr(ferramentas, "adicionar_evento", enviar)
    resultado = asyncio.run(ferramentas.criar_evento.coroutine(SimpleNamespace(context=contexto_evento)))
    assert resultado["status"] in {"CONFIRMACAO_NECESSARIA", "RASCUNHO_INDISPONIVEL"}
    preparar.assert_not_awaited()
    enviar.assert_not_awaited()


@pytest.mark.parametrize("mensagem,campos", [
    ("Confirmo o início", {"data_hora_inicio"}), ("Confirmo o fim", {"data_hora_fim"}),
    ("Confirmo os horários", {"data_hora_inicio", "data_hora_fim"}),
    ("Confirmo a observação", {"observacao"}), ("Confirmo a descrição", {"descricao"}),
    ("Confirmo o local", {"local_unidade_id", "descricao_local"}),
])
def test_aceites_parciais_identificam_campos(proposta_evento, contexto_evento, mensagem, campos):
    contexto_evento["mensagem_atual"] = mensagem
    resultado = avaliar_confirmacao(proposta_evento, contexto_evento)
    assert resultado["status"] == "CONFIRMACAO_PARCIAL"
    assert set(resultado["campos_confirmados"]) == campos


@pytest.mark.parametrize("mensagem,manifestacao", [
    ("Pode criar o evento", "aceite"), ("Confirmo o evento", "aceite"),
    ("Cancelar o evento", "cancelamento"), ("Não quero continuar o evento", "cancelamento"),
    ("Pausar o evento", "pausa"), ("Retomar o evento", "retomada"),
    ("Sim, mas mude o início", "negacao"),
])
def test_vocabulario_de_eventos(mensagem, manifestacao):
    assert classificar_manifestacao(mensagem) == manifestacao


def test_aceite_de_outro_cadastro_nao_confirma_evento(proposta_evento, contexto_evento):
    contexto_evento["mensagem_atual"] = "Pode criar a solicitação"
    assert avaliar_confirmacao(proposta_evento, contexto_evento)["status"] == "CONFIRMACAO_NECESSARIA"
    saida = asyncio.run(continuacoes.tratar_continuacao(
        {"evento_pendente": proposta_evento}, contexto_evento, contexto_evento["mensagem_atual"],
    ))
    assert saida["esclarecimento_roteamento"]


def test_sim_continua_evento_e_resposta_publica_aceita_intencao(proposta_evento, contexto_evento):
    saida = asyncio.run(continuacoes.tratar_continuacao({"evento_pendente": proposta_evento}, contexto_evento, "Sim"))
    assert saida["intencao"] == "evento"
    assert ConversaSaida(thread_id="sessao", intencao="evento", resposta="Confira").intencao == "evento"


@pytest.mark.parametrize("status", ["enviando", "resultado_indeterminado"])
def test_envio_incerto_bloqueia_nova_preparacao(monkeypatch, contexto_evento, proposta_evento, status):
    proposta_evento["status_fluxo"] = status
    monkeypatch.setattr(ferramentas, "obter_rascunho_solicitacao", AsyncMock(return_value=proposta_evento))
    enviar = AsyncMock()
    monkeypatch.setattr(ferramentas, "adicionar_evento", enviar)
    resultado = asyncio.run(ferramentas.processar_evento(
        SimpleNamespace(context=contexto_evento), operacao_aprovada=dados_cadastro(proposta_evento),
    ))
    assert resultado["status"] == "RESULTADO_INDETERMINADO"
    enviar.assert_not_awaited()


@pytest.fixture
def operacoes_evento(monkeypatch):
    """Exercita o protocolo durável real com uma coleção local simulada."""
    persistencia = import_module("app.memory.persistencia.operacoes")
    registros = {}

    class Colecao:
        async def find_one(self, filtro):
            documento = registros.get(filtro["_id"])
            if documento is not None and all(documento.get(k) == v for k, v in filtro.items()):
                return deepcopy(documento)
            return None

        async def update_one(self, filtro, atualizacao, upsert=False):
            documento = registros.get(filtro["_id"])
            if documento is None and upsert:
                registros[filtro["_id"]] = deepcopy(atualizacao["$setOnInsert"])
                return SimpleNamespace(matched_count=0)
            if documento is not None and all(documento.get(k) == v for k, v in filtro.items()):
                documento.update(deepcopy(atualizacao.get("$set", {})))
                return SimpleNamespace(matched_count=1)
            return SimpleNamespace(matched_count=0)

    @asynccontextmanager
    async def mongo():
        yield {persistencia.MONGO_BANCO_DADOS: {persistencia.COLECAO: Colecao()}}

    monkeypatch.setattr(persistencia, "abrir_cliente_mongo", mongo)
    return registros


@pytest.fixture
def motor_evento(monkeypatch, proposta_evento, local_evento, operacoes_evento):
    async def atualizar(sessao, usuario, campos, **controle):
        if (proposta_evento["status_fluxo"] not in controle["status_esperados"]
                or proposta_evento["versao"] != controle["versao"] or proposta_evento.get("pausado")):
            return False
        assert controle["tipo"] == "evento" and controle["rascunho_id"] == proposta_evento["id"]
        proposta_evento.update(deepcopy(campos))
        return True

    monkeypatch.setattr(ferramentas, "obter_rascunho_solicitacao", AsyncMock(side_effect=lambda *a, **k: deepcopy(proposta_evento)))
    monkeypatch.setattr(ferramentas, "atualizar_rascunho_solicitacao", atualizar)
    enviar = AsyncMock(return_value={"status": "SUCESSO", "evento_id": 15})
    monkeypatch.setattr(ferramentas, "adicionar_evento", enviar)
    return enviar


def estado_aprovado(contexto):
    operacoes = deepcopy(contexto["operacoes_pendentes"])
    return {"operacoes_pendentes": operacoes, "veredito": "aprovado",
            "aprovacao_operacoes": aprovacao_operacoes(operacoes, contexto)}


@pytest.mark.parametrize("decisao", ["aprovado", "bloqueado", "revisar", "indisponivel"])
@pytest.mark.parametrize("perfil,plataforma", [
    ("gestor", "web"), ("gestor", "mobile"), ("administrador", "web"), ("administrador", "mobile"),
])
def test_grafo_so_envia_evento_apos_juiz(
    monkeypatch, contexto_evento, proposta_evento, motor_evento, decisao, perfil, plataforma,
):
    from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
    from app.graph import fluxo, nos
    from app.graph.executor import criar_estado_inicial
    juiz = import_module("app.agents.juiz")
    contexto_evento["usuario"].tipo_acesso = perfil
    contexto_evento["plataforma"] = plataforma
    etapas = []

    async def agente(entrada, *, context):
        resultado = await ferramentas.criar_evento.coroutine(SimpleNamespace(context=context))
        motor_evento.assert_not_awaited()
        assert resultado["status"] == "OPERACAO_PREPARADA"
        etapas.append("preparado")
        return {"messages": [
            AIMessage(content="", tool_calls=[{"name": "criar_evento", "id": "chamada", "args": {}}]),
            ToolMessage(content=json.dumps(resultado), tool_call_id="chamada"),
        ], "structured_response": SolicitacaoOcorrenciaResultado(
            agente="solicitacoes", resposta="Evento preparado.", status="OPERACAO_PREPARADA",
        )}

    async def julgar(dados, perguntas, **kwargs):
        motor_evento.assert_not_awaited()
        assert dados["operacoes_pendentes"][0]["tipo"] == "evento"
        assert dados["operacoes_pendentes"][0]["dados"]["dados"] == proposta_evento["dados"]
        etapas.append("julgado")
        if decisao == "indisponivel":
            raise ConnectionError("Juiz indisponível")
        veredito = "aprovado" if decisao == "revisar" and etapas.count("julgado") == 2 else decisao
        return {"answers": {
            "veredito": {"type": "choice", "choice": veredito, "confidence": .95},
            "motivo": {"type": "choice", "choice": "nenhum" if veredito == "aprovado" else "clareza", "confidence": .95},
            "afirmacao_sem_suporte": {"type": "noul", "noul": .05},
            "correcao_textual": {"type": "noul", "noul": .05},
            "risco_grave": {"type": "noul", "noul": .05},
        }}

    monkeypatch.setattr(nos, f"solicitacoes_{perfil}", SimpleNamespace(ainvoke=agente))
    monkeypatch.setattr(nos, "obter_rascunho_solicitacao", AsyncMock(return_value=proposta_evento))
    monkeypatch.setattr(juiz, "consultar_jev", julgar)
    monkeypatch.setattr(fluxo, "validar_entrada", lambda estado: {"entrada_valida": True})
    monkeypatch.setattr(fluxo, "classificar_emocao", AsyncMock(return_value={"emocao": "NEUTRO"}))
    monkeypatch.setattr(fluxo, "revisar_resposta", AsyncMock(return_value={
        "resposta_especialista": "Dados preparados para cadastro do evento.", "erro": None,
    }))
    grafo = fluxo.construir_grafo()
    estado = criar_estado_inicial([HumanMessage(content="Pode criar o evento")], contexto_evento["usuario"])
    estado["evento_pendente"] = proposta_evento
    saida = asyncio.run(grafo.ainvoke(estado, config={"configurable": {"thread_id": "teste"}}, context=contexto_evento))
    assert etapas == ["preparado", "julgado"] + (["julgado"] if decisao == "revisar" else [])
    if decisao in {"aprovado", "revisar"}:
        assert saida["resposta_final"] == "Evento cadastrado com sucesso."
        motor_evento.assert_awaited_once()
        assert motor_evento.await_args.kwargs == {"usuario_id": 7}
        assert motor_evento.await_args.args[1] == "token-teste"
        assert proposta_evento["status_fluxo"] == "cadastrada"
    else:
        motor_evento.assert_not_awaited()
        assert not saida.get("resultados_operacoes")


@pytest.mark.parametrize("resultado_api", ["SUCESSO", "RESULTADO_INDETERMINADO"])
def test_executor_nao_repete_post(monkeypatch, contexto_evento, proposta_evento, motor_evento, resultado_api):
    from app.graph.operacoes import executar_operacoes
    motor_evento.return_value = {"status": resultado_api, "evento_id": 15}

    async def verificar():
        runtime = SimpleNamespace(context=contexto_evento)
        preparado = await ferramentas.criar_evento.coroutine(runtime)
        assert preparado["status"] == "OPERACAO_PREPARADA"
        motor_evento.assert_not_awaited()
        estado = estado_aprovado(contexto_evento)
        await executar_operacoes(estado, runtime)
        await executar_operacoes(estado, runtime)
        assert proposta_evento["status_fluxo"] == (
            "cadastrada" if resultado_api == "SUCESSO" else "resultado_indeterminado"
        )

    asyncio.run(verificar())
    motor_evento.assert_awaited_once()


@pytest.mark.parametrize("alteracao", ["titulo", "versao", "usuario", "turno", "local"])
def test_alteracao_apos_aprovacao_impede_envio(contexto_evento, proposta_evento, motor_evento, alteracao):
    from app.graph.operacoes import executar_operacoes

    async def verificar():
        runtime = SimpleNamespace(context=contexto_evento)
        await ferramentas.criar_evento.coroutine(runtime)
        estado = estado_aprovado(contexto_evento)
        if alteracao in {"titulo", "local"}:
            campo, valor = ("titulo", "Outro evento") if alteracao == "titulo" else ("local_unidade_id", 99)
            proposta_evento["dados"][campo] = valor
        elif alteracao == "versao":
            proposta_evento["versao"] = 2
        elif alteracao == "usuario":
            contexto_evento["usuario"] = contexto_evento["usuario"].model_copy(update={"usuario_id": 8})
        else:
            contexto_evento["turno_id"] = "outro"
        await executar_operacoes(estado, runtime)

    asyncio.run(verificar())
    motor_evento.assert_not_awaited()


def test_confirmacao_parcial_persiste_somente_campos_aceitos(contexto_evento, proposta_evento, motor_evento):
    contexto_evento["mensagem_atual"] = "Confirmo os horários"
    resultado = asyncio.run(ferramentas.criar_evento.coroutine(SimpleNamespace(context=contexto_evento)))
    assert resultado["status"] == "CONFIRMACAO_PARCIAL"
    assert set(proposta_evento["dados_confirmados"]) == {"data_hora_inicio", "data_hora_fim"}
    assert "Início:" not in resultado["proposta"]["resumo_confirmacao"]
    assert "Título:" in resultado["proposta"]["resumo_confirmacao"]
    motor_evento.assert_not_awaited()


def test_coleta_correcao_e_arquivo_de_evento_preservam_outros_rascunhos(monkeypatch):
    persistencia = import_module("app.memory.persistencia.rascunho_solicitacao")
    documento = {"evento_pendente": None, "anexos_pendentes": ["foto"],
                 "ocorrencia_pendente": {"status_fluxo": "coletando_dados", "imagens": ["foto-ocorrencia"]}}
    colecao = SimpleNamespace(find_one=AsyncMock(side_effect=lambda *a, **k: deepcopy(documento)),
                             update_one=AsyncMock(return_value=SimpleNamespace(matched_count=1)))

    @asynccontextmanager
    async def mongo():
        yield {persistencia.MONGO_BANCO_DADOS: {persistencia.MONGO_COLECAO_SESSOES: colecao}}

    monkeypatch.setattr(persistencia, "abrir_cliente_mongo", mongo)
    monkeypatch.setattr(persistencia, "obter_documento_sessao_id", AsyncMock(return_value="documento"))

    async def verificar():
        coleta = await persistencia.registrar_coleta_parcial("sessao", 7, tipo="evento", turno_id="coleta", relato="Evento no auditório")
        assert coleta["imagens"] == [] and coleta["relatos"][0]["texto"] == "Evento no auditório"
        assert "$unset" not in colecao.update_one.await_args.args[1]
        documento["evento_pendente"] = coleta
        dados = CriarEventoEntrada(**dados_evento()).model_dump(mode="json")
        proposta = await persistencia.salvar_rascunho_solicitacao("sessao", 7, dados, tipo="evento", turno_id="proposta")
        assert proposta["id"] == coleta["id"] and proposta["versao"] == 2
        assert proposta["relatos"] == coleta["relatos"] and not proposta["imagens"]
        proposta["dados_confirmados"] = proposta["dados"].copy()
        documento["evento_pendente"] = proposta
        corrigida = await persistencia.salvar_rascunho_solicitacao(
            "sessao", 7, {**dados, "observacao": "Trazer material"}, tipo="evento", turno_id="correcao",
        )
        assert corrigida["versao"] == 3 and "observacao" not in corrigida["dados_confirmados"]
        assert corrigida["dados_confirmados"]["titulo"] == dados["titulo"]
        assert "turno_apresentacao" not in corrigida
        corrigida["status_fluxo"] = "cadastrada"
        documento["evento_pendente"] = corrigida
        nova = await persistencia.registrar_coleta_parcial("sessao", 7, tipo="evento", turno_id="novo", relato="Outro evento")
        assert nova["id"] != corrigida["id"]
        assert colecao.update_one.await_args.args[1]["$push"] == {"eventos": corrigida}
        assert documento["anexos_pendentes"] == ["foto"]
        assert documento["ocorrencia_pendente"]["imagens"] == ["foto-ocorrencia"]

    asyncio.run(verificar())


@pytest.mark.parametrize("perfil", ["gestor", "administrador", "tecnico", "solicitante"])
def test_ferramentas_de_evento_sao_conectadas_apenas_aos_perfis_autorizados(monkeypatch, perfil):
    fabrica = import_module("app.agents.solicitacoes")
    criar = Mock()
    monkeypatch.setattr(fabrica, "create_agent", criar)
    fabrica.criar_agente_solicitacoes(
        modelo=Mock(), instrucao="teste", gestor=perfil in {"gestor", "administrador"},
        tecnico=perfil == "tecnico", solicitante=perfil == "solicitante",
    )
    nomes = {t.name for t in criar.call_args.kwargs["tools"]}
    eventos = {"buscar_opcoes_evento", "salvar_rascunho_evento", "criar_evento"}
    assert (nomes & eventos) == (eventos if perfil in {"gestor", "administrador"} else set())
    schema = ferramentas.salvar_rascunho_evento.tool_call_schema.model_json_schema()
    assert not {"runtime", "usuario_id", "access_token", "usuarioId"} & schema["properties"].keys()


def test_coleta_e_retomo_do_rascunho_sao_injetados_sem_exigir_foto(monkeypatch, contexto_evento):
    from langchain_core.messages import HumanMessage, SystemMessage
    from app.graph import nos
    parcial = {"id": "rascunho", "tipo": "evento", "versao": 1,
               "status_fluxo": "coletando_dados", "dados": {}, "imagens": [],
               "relatos": [{"turno_id": "coleta", "texto": "Evento no auditório amanhã"}]}
    registrar = AsyncMock(return_value=parcial)
    anexar = AsyncMock()
    monkeypatch.setattr(nos, "registrar_coleta_parcial", registrar)
    monkeypatch.setattr(nos, "adicionar_imagens_sessao", anexar)
    monkeypatch.setattr(nos, "obter_rascunho_solicitacao", AsyncMock(return_value=parcial))
    contexto_evento["imagens"] = ["foto"]

    async def executar(agente, estado, contexto, formato):
        textos = [m.content for m in estado["messages"] if isinstance(m, SystemMessage)]
        assert any("Evento no auditório amanhã" in texto for texto in textos)
        assert any("não peça foto" in texto for texto in textos)
        assert contexto["intencao_atual"] == "evento"
        return {"structured_response": SolicitacaoOcorrenciaResultado(
            agente="solicitacoes", resposta="Quais são os horários de início e fim?", status="AGUARDANDO_INFORMACAO",
        )}, []

    monkeypatch.setattr(nos, "executar_com_evidencias", executar)
    resultado = asyncio.run(nos.executar_solicitacao(
        {"perfil": "gestor", "intencao": "evento", "cadastro_em_andamento": True,
         "messages": [HumanMessage(content="Evento no auditório amanhã")], "evidencias": []},
        SimpleNamespace(context=contexto_evento),
    ))
    assert resultado["erro"] is None
    assert registrar.await_args.kwargs["tipo"] == "evento"
    anexar.assert_not_awaited()


@pytest.mark.parametrize("mensagem", ["Pausar o evento", "Cancelar o evento", "Retomar o evento"])
def test_continuacao_atualiza_somente_proposta_de_evento(monkeypatch, contexto_evento, proposta_evento, mensagem):
    atualizar = AsyncMock(return_value=True)
    monkeypatch.setattr(continuacoes, "atualizar_rascunho_solicitacao", atualizar)
    resultado = asyncio.run(continuacoes.tratar_continuacao(
        {"evento_pendente": proposta_evento}, contexto_evento, mensagem,
    ))
    assert atualizar.await_args.kwargs["tipo"] == "evento"
    proposta = resultado["evento_pendente"]
    if mensagem.startswith("Retomar"):
        assert resultado["intencao"] == "evento" and not proposta["pausado"]
    else:
        assert proposta["pausado"]
        assert proposta["status_fluxo"] == ("cancelada" if mensagem.startswith("Cancelar") else "aguardando_confirmacao")


@pytest.mark.parametrize("falhar_persistencia", [False, True])
def test_confirmacao_publica_depende_de_proposta_apresentada_e_persistida(
    monkeypatch, contexto_evento, proposta_evento, falhar_persistencia,
):
    from app.graph import executor
    proposta = metadados_proposta(proposta_evento)
    retorno = {"resposta_final": proposta["resumo_confirmacao"], "propostas_apresentadas": [proposta], "intencao": "evento"}
    monkeypatch.setattr(executor, "grafo", SimpleNamespace(
        get_state=lambda _: SimpleNamespace(values={}), ainvoke=AsyncMock(return_value=retorno),
    ))
    for nome, valor in {
        "obter_documento_sessao_id": "documento", "recuperar_mensagens": [],
        "obter_rascunho_solicitacao": proposta_evento, "obter_acao": None,
        "obter_analise_compra": None, "obter_quantidade_anexos_pendentes": 0,
    }.items():
        monkeypatch.setattr(executor, nome, AsyncMock(return_value=valor))
    sequencia = []

    async def salvar(sessao, papel, *args, **kwargs):
        sequencia.append(papel)
        if papel == "assistant" and falhar_persistencia:
            raise ConnectionError("Falha ao salvar resposta")

    async def apresentar(*args, **kwargs):
        assert sequencia[-1] == "assistant"
        assert kwargs["tipo"] == "evento"
        assert args[2]["dados_apresentados"] == proposta["dados"]
        sequencia.append("apresentada")
        return True

    monkeypatch.setattr(executor, "salvar_mensagem", salvar)
    marcar = AsyncMock(side_effect=apresentar)
    monkeypatch.setattr(executor, "atualizar_rascunho_solicitacao", marcar)
    marcar_botao = AsyncMock()
    monkeypatch.setattr(executor, "marcar_confirmacao_mensagem", marcar_botao)
    chamada = executor.executar_grafo("Criar evento", contexto_evento["usuario"], "sessao")
    if falhar_persistencia:
        with pytest.raises(ConnectionError):
            asyncio.run(chamada)
        marcar.assert_not_awaited()
        marcar_botao.assert_not_awaited()
    else:
        resultado = asyncio.run(chamada)
        assert resultado["confirmacao"] == "sim"
        assert sequencia == ["human", "assistant", "apresentada"]
        marcar_botao.assert_awaited_once()
