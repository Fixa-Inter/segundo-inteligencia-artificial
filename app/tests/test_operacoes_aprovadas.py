"""Gravações só acontecem após aprovação; falhas posteriores preservam o resultado."""

import asyncio
import json
from contextlib import asynccontextmanager
from copy import deepcopy
from datetime import datetime, timezone
from importlib import import_module
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from langchain_core.messages import HumanMessage

from app.graph import operacoes as executor
from app.graph import nos
from app.graph.transicoes import decidir_apos_julgamento
from app.memory.persistencia import operacoes as persistencia
from app.schemas import UsuarioContexto
from app.services.operacoes import aprovacao_operacoes, dados_cadastro, preparar_operacao


@pytest.fixture
def contexto():
    return {"usuario": UsuarioContexto.model_construct(
        usuario_id=7, tipo_acesso="tecnico", access_token="teste",
    ), "session_id": "sessao", "turno_id": "confirmacao",
        "mensagem_atual": "Pode registrar", "imagens": [], "operacoes_pendentes": []}


@pytest.fixture
def documentos(monkeypatch):
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
    async def abrir_cliente():
        yield {persistencia.MONGO_BANCO_DADOS: {persistencia.COLECAO: Colecao()}}

    monkeypatch.setattr(persistencia, "abrir_cliente_mongo", abrir_cliente)
    return registros


def estado_aprovado(contexto):
    operacoes = deepcopy(contexto["operacoes_pendentes"])
    return {"operacoes_pendentes": operacoes, "veredito": "aprovado",
            "aprovacao_operacoes": aprovacao_operacoes(operacoes, contexto)}


def test_preparacao_repetida_nao_grava_feedback_e_rejeita_dados_divergentes(monkeypatch, contexto, documentos):
    ferramenta = import_module("app.tools.feedback.criarFeedback")
    servico = import_module("app.services.feedback.criar_feedback")
    inserir = AsyncMock()
    monkeypatch.setattr(servico, "executar_insercao", inserir)

    async def verificar():
        runtime = SimpleNamespace(context=contexto)
        a = await ferramenta.criar_nome_feedback.coroutine("Sugestão de filtro", "Melhoria", runtime)
        b = await ferramenta.criar_nome_feedback.coroutine("Sugestão de filtro", "Melhoria", runtime)
        assert a == b and a["status"] == "OPERACAO_PREPARADA"
        with pytest.raises(ValueError, match="mudou"):
            await ferramenta.criar_nome_feedback.coroutine("Outro texto", "Melhoria", runtime)

    asyncio.run(verificar())
    inserir.assert_not_awaited()
    assert len(documentos) == len(contexto["operacoes_pendentes"]) == 1


@pytest.mark.parametrize("tipo", ["solicitacao", "ocorrencia"])
@pytest.mark.parametrize("falhar_atualizacao", [False, True])
def test_cadastro_prepara_sem_post_e_so_executor_envia(monkeypatch, tipo, contexto, documentos, falhar_atualizacao):
    modulo = import_module("app.tools." + (
        "solicitacoes.criarSolicitacao" if tipo == "solicitacao" else "ocorrencias.criarOcorrencia"
    ))
    dados = {"titulo": "Ventilador", "local_endereco_id": 2, "categoria_equipamento_id": 3,
             "descricao_local": "Sala 2"}
    dados.update({"descricao_problema": "Não liga"} if tipo == "solicitacao" else {
        "descricao_ocorrencia": "Troquei o motor", "categoria_problema_id": "MECANICA", "prioridade": "BAIXA",
    })
    rascunho = {"id": "proposta", "versao": 1, "tipo": tipo, "turno_id": "antes",
                "turno_apresentacao": "apresentacao", "versao_apresentada": 1,
                "dados_apresentados": dados.copy(), "dados": dados,
                "status_fluxo": "aguardando_confirmacao", "imagens": ["https://example.com/foto.jpg"]}
    monkeypatch.setattr(modulo, "obter_rascunho_solicitacao", AsyncMock(return_value=rascunho))

    async def atualizar(sessao, usuario, campos, **controle):
        if falhar_atualizacao and campos.get("status_fluxo") == "cadastrada":
            raise ConnectionError("Mongo indisponível depois do sucesso da API")
        if rascunho["status_fluxo"] not in controle["status_esperados"]:
            return False
        rascunho.update(campos)
        return True

    monkeypatch.setattr(modulo, "atualizar_rascunho_solicitacao", atualizar)
    monkeypatch.setattr(modulo, "obter_unidade_id", AsyncMock(return_value=1))
    monkeypatch.setattr(modulo, "validar_selecao", AsyncMock())

    @asynccontextmanager
    async def qdrant():
        yield object()

    monkeypatch.setattr(modulo, "abrir_cliente_qdrant", qdrant)
    enviar = AsyncMock(return_value={"status": "SUCESSO"})
    monkeypatch.setattr(modulo, f"adicionar_{tipo}", enviar)

    async def verificar():
        resultado = await getattr(modulo, f"criar_{tipo}").coroutine(SimpleNamespace(context=contexto))
        assert resultado["status"] == "OPERACAO_PREPARADA"
        enviar.assert_not_awaited()
        aprovado = estado_aprovado(contexto)
        saida = await executor.executar_operacoes(aprovado, SimpleNamespace(context=contexto))
        assert "com sucesso" in saida["resposta_final"]
        await executor.executar_operacoes(aprovado, SimpleNamespace(context=contexto))

    asyncio.run(verificar())
    enviar.assert_awaited_once()


@pytest.mark.parametrize("veredito", ["bloqueado", "revisar"])
def test_sem_aprovacao_nao_executa(monkeypatch, contexto, documentos, veredito):
    executar = AsyncMock()
    monkeypatch.setattr(executor, "executar_servico", executar)

    async def verificar():
        await preparar_operacao(contexto, "feedback", "mensagem", {"comentario": "Teste"})
        estado = {**estado_aprovado(contexto), "veredito": veredito}
        assert decidir_apos_julgamento(estado) != "executar_operacoes"
        await executor.executar_operacoes(estado, SimpleNamespace(context=contexto))

    asyncio.run(verificar())
    executar.assert_not_awaited()


@pytest.mark.parametrize("alteracao", ["dados", "anexos", "usuario", "turno"])
def test_aprovacao_nao_serve_para_outros_dados_ou_contextos(monkeypatch, contexto, documentos, alteracao):
    executar = AsyncMock()
    monkeypatch.setattr(executor, "executar_servico", executar)

    async def verificar():
        await preparar_operacao(contexto, "solicitacao", "proposta", {"titulo": "Antes", "imagens": ["a"]})
        estado = estado_aprovado(contexto)
        if alteracao == "dados":
            estado["operacoes_pendentes"][0]["dados"]["titulo"] = "Depois"
        elif alteracao == "anexos":
            estado["operacoes_pendentes"][0]["dados"]["imagens"].append("b")
        elif alteracao == "usuario":
            contexto["usuario"] = contexto["usuario"].model_copy(update={"usuario_id": 8})
        else:
            contexto["turno_id"] = "outro"
        await executor.executar_operacoes(estado, SimpleNamespace(context=contexto))

    asyncio.run(verificar())
    executar.assert_not_awaited()


def test_duas_execucoes_concorrentes_nao_repetem_gravacao(monkeypatch, contexto, documentos):
    async def gravar(documento, contexto):
        # Permite que a segunda execução encontre a primeira ainda em andamento.
        await asyncio.sleep(0)
        return {"status": "SUCESSO"}

    executar = AsyncMock(side_effect=gravar)
    monkeypatch.setattr(executor, "executar_servico", executar)

    async def verificar():
        await preparar_operacao(contexto, "feedback", "mensagem", {"comentario": "Teste"})
        estado = estado_aprovado(contexto)
        await asyncio.gather(
            executor.executar_operacoes(estado, SimpleNamespace(context=contexto)),
            executor.executar_operacoes(estado, SimpleNamespace(context=contexto)),
        )

    asyncio.run(verificar())
    executar.assert_awaited_once()


def test_timeout_nao_libera_reenvio(monkeypatch, contexto, documentos):
    executar = AsyncMock(side_effect=TimeoutError("Resposta perdida"))
    monkeypatch.setattr(executor, "executar_servico", executar)

    async def verificar():
        await preparar_operacao(contexto, "feedback", "mensagem", {"comentario": "Teste"})
        estado = estado_aprovado(contexto)
        for _ in range(2):
            saida = await executor.executar_operacoes(estado, SimpleNamespace(context=contexto))
            assert "pode ter ocorrido" in saida["resposta_final"]
        assert next(iter(documentos.values()))["estado"] == "indeterminada"

    asyncio.run(verificar())
    executar.assert_awaited_once()


def test_falha_no_mongo_depois_do_sucesso_preserva_confirmacao(monkeypatch, contexto, documentos):
    executar = AsyncMock(return_value={"status": "SUCESSO"})
    monkeypatch.setattr(executor, "executar_servico", executar)
    monkeypatch.setattr(persistencia, "finalizar", AsyncMock(side_effect=ConnectionError()))

    async def verificar():
        await preparar_operacao(contexto, "feedback", "mensagem", {"comentario": "Teste"})
        estado = estado_aprovado(contexto)
        saida = await executor.executar_operacoes(estado, SimpleNamespace(context=contexto))
        assert saida["resposta_final"] == "Feedback registrado com sucesso."
        assert contexto["resultados_operacoes"][0]["resultado"]["status"] == "SUCESSO"
        await executor.executar_operacoes(estado, SimpleNamespace(context=contexto))

    asyncio.run(verificar())
    executar.assert_awaited_once()


@pytest.mark.parametrize("tipo", ["alteracao", "solicitacao", "ocorrencia", "observacao_conclusao"])
def test_edicoes_e_anexos_aguardam_aprovacao(monkeypatch, contexto, documentos, tipo):
    edicoes = import_module("app.tools.ajuda_geral.edicoes")
    acao = {"id": "edicao", "tipo": tipo, "registro_id": 10,
            "campo": "titulo", "novo_valor": "Novo título", "imagens": ["https://example.com/foto.jpg"],
            "status": "aguardando_confirmacao", "turno_id": "antes",
            "criada_em": datetime.now(timezone.utc)}
    contexto["mensagem_atual"] = "Pode alterar" if tipo == "alteracao" else "Pode anexar"
    alterar = AsyncMock(return_value={"id": 10})
    anexar = AsyncMock(return_value=[12])
    monkeypatch.setattr(edicoes.servico, "alterar_solicitacao", alterar)
    monkeypatch.setattr(edicoes.servico, "anexar_fotos", anexar)
    monkeypatch.setattr(edicoes, "iniciar_acao", AsyncMock(return_value=True))
    monkeypatch.setattr(edicoes, "atualizar_acao", AsyncMock(side_effect=ConnectionError()))
    monkeypatch.setattr(import_module("app.memory.persistencia"), "obter_acao", AsyncMock(return_value=acao))

    async def verificar():
        resultado = await edicoes._executar_pendente(contexto, contexto["usuario"], "sessao", acao)
        assert resultado["status"] == "OPERACAO_PREPARADA"
        alterar.assert_not_awaited()
        anexar.assert_not_awaited()
        saida = await executor.executar_operacoes(estado_aprovado(contexto), SimpleNamespace(context=contexto))
        assert "sucesso" in saida["resposta_final"]

    asyncio.run(verificar())
    (alterar if tipo == "alteracao" else anexar).assert_awaited_once()


def test_falha_do_agente_apos_preparar_nao_grava_e_juiz_bloqueia(monkeypatch, contexto, documentos):
    from app.graph import nos
    juiz = import_module("app.agents.juiz")
    servico = AsyncMock()
    monkeypatch.setattr(executor, "executar_servico", servico)

    async def agente(entrada, *, context):
        await preparar_operacao(context, "feedback", "mensagem", {"comentario": "Teste"})
        raise RuntimeError("Falha após preparar")

    monkeypatch.setattr(nos, "feedback", SimpleNamespace(ainvoke=agente))

    async def verificar():
        estado = {"perfil": "tecnico", "messages": [], "evidencias": []}
        estado.update(await nos.executar_retorno_usuario(estado, SimpleNamespace(context=contexto)))
        estado.update(await juiz.julgar_resposta(estado, SimpleNamespace(context=contexto)))
        assert estado["veredito"] == "bloqueado"
        assert len(estado["operacoes_pendentes"]) == 1
        assert estado["aprovacao_operacoes"] is None
        assert next(iter(documentos.values()))["estado"] == "preparada"

    asyncio.run(verificar())
    servico.assert_not_awaited()


@pytest.mark.parametrize("decisao", ["aprovado", "bloqueado", "indisponivel", "revisar"])
def test_grafo_completo_executa_feedback_somente_apos_juiz(monkeypatch, contexto, documentos, decisao):
    from langchain_core.messages import AIMessage, ToolMessage
    from app.agents.agentsResult import RetornoUsuarioResultado
    from app.graph import fluxo
    from app.graph.executor import criar_estado_inicial
    juiz = import_module("app.agents.juiz")
    ferramenta = import_module("app.tools.feedback.criarFeedback")
    servico = import_module("app.services.feedback")
    gravar = AsyncMock(return_value={"status": "SUCESSO", "feedback_id": 10})
    eventos = []
    monkeypatch.setattr(servico, "criar_feedback", gravar)

    async def agente(entrada, *, context):
        resultado = await ferramenta.criar_nome_feedback.coroutine(
            "Sugestão de filtro", "Melhoria", SimpleNamespace(context=context),
        )
        gravar.assert_not_awaited()
        eventos.append("preparado")
        return {"messages": [
            AIMessage(content="", tool_calls=[{"name": "criar_nome_feedback", "id": "chamada", "args": {}}]),
            ToolMessage(content=json.dumps(resultado), tool_call_id="chamada"),
        ], "structured_response": RetornoUsuarioResultado(
            agente="feedback", resposta="Comentário preparado.", status="OPERACAO_PREPARADA",
        )}

    async def julgar(dados, perguntas, **kwargs):
        gravar.assert_not_awaited()
        assert dados["operacoes_pendentes"][0]["dados"]["comentario"] == "Sugestão de filtro"
        eventos.append("julgado")
        if decisao == "indisponivel":
            raise ConnectionError("Juiz indisponível")
        veredito = "aprovado" if decisao == "revisar" and eventos.count("julgado") == 2 else decisao
        return {"answers": {
            "veredito": {"type": "choice", "choice": veredito, "confidence": .95},
            "motivo": {"type": "choice", "choice": "nenhum" if veredito == "aprovado" else "clareza", "confidence": .95},
            "afirmacao_sem_suporte": {"type": "noul", "noul": .05},
            "correcao_textual": {"type": "noul", "noul": .05},
            "risco_grave": {"type": "noul", "noul": .05},
        }}

    monkeypatch.setattr(nos, "feedback", SimpleNamespace(ainvoke=agente))
    monkeypatch.setattr(juiz, "consultar_jev", julgar)
    monkeypatch.setattr(fluxo, "validar_entrada", lambda estado: {"entrada_valida": True})
    monkeypatch.setattr(fluxo, "supervisionar", lambda estado: {"intencao": "feedback"})
    monkeypatch.setattr(fluxo, "classificar_emocao", AsyncMock(return_value={"emocao": "NEUTRO"}))
    monkeypatch.setattr(fluxo, "revisar_resposta", AsyncMock(return_value={
        "resposta_especialista": "Comentário preparado para registro.", "erro": None,
    }))
    grafo = fluxo.construir_grafo()

    async def verificar():
        estado = criar_estado_inicial([HumanMessage(content="Registre esta sugestão")], contexto["usuario"])
        saida = await grafo.ainvoke(estado, config={"configurable": {"thread_id": "teste"}}, context=contexto)
        if decisao in {"aprovado", "revisar"}:
            assert saida["resposta_final"] == "Feedback registrado com sucesso."
            gravar.assert_awaited_once()
        else:
            gravar.assert_not_awaited()
            assert not saida.get("resultados_operacoes")
        assert eventos == ["preparado", "julgado"] + (["julgado"] if decisao == "revisar" else [])

    asyncio.run(verificar())


@pytest.mark.parametrize("falha", ["grafo", "historico", "protecao_saida"])
def test_resultado_real_sobrevive_a_falha_posterior(monkeypatch, contexto, falha):
    from app.graph import executor as chat
    for nome in ("obter_rascunho_solicitacao", "obter_acao", "obter_analise_compra"):
        monkeypatch.setattr(chat, nome, AsyncMock(return_value=None))
    monkeypatch.setattr(chat, "obter_quantidade_anexos_pendentes", AsyncMock(return_value=0))
    monkeypatch.setattr(chat, "obter_documento_sessao_id", AsyncMock(return_value="documento"))
    monkeypatch.setattr(chat, "recuperar_mensagens", AsyncMock(return_value=[]))

    async def executar(estado, *, config, context):
        resultados = [{"operacao_id": "acao", "tipo": "feedback", "resultado": {"status": "SUCESSO"}}]
        context["resultados_operacoes"] = resultados
        if falha == "grafo":
            raise RuntimeError("Falha depois da gravação")
        if falha == "protecao_saida":
            return {"erro": "Falha na apresentação", "resposta_final": "Não foi possível revisar a resposta."}
        return {**executor.resposta_resultados(resultados), "intencao": "feedback"}

    async def salvar(sessao, papel, *args, **kwargs):
        if papel == "assistant" and falha == "historico":
            raise ConnectionError("Histórico indisponível")

    monkeypatch.setattr(chat, "grafo", SimpleNamespace(
        get_state=lambda config: SimpleNamespace(values={}), ainvoke=executar,
    ))
    monkeypatch.setattr(chat, "salvar_mensagem", salvar)
    resultado = asyncio.run(chat.executar_grafo("Registre", contexto["usuario"], "sessao"))
    assert resultado["resposta_final"].startswith("Feedback registrado com sucesso.")
    assert resultado["confirmacao"] == "nao"


def test_resultados_parciais_sao_informados_separadamente(monkeypatch, contexto, documentos):
    executar = AsyncMock(side_effect=[{"status": "SUCESSO"}, {"status": "ERRO_VALIDACAO"}])
    monkeypatch.setattr(executor, "executar_servico", executar)

    async def verificar():
        await preparar_operacao(contexto, "feedback", "comentario", {"comentario": "Teste"})
        await preparar_operacao(contexto, "edicao", "alteracao", {"campo": "titulo"})
        resultado = await executor.executar_operacoes(estado_aprovado(contexto), SimpleNamespace(context=contexto))
        assert "Feedback registrado com sucesso." in resultado["resposta_final"]
        assert "A alteração não foi realizada." in resultado["resposta_final"]

    asyncio.run(verificar())


def test_retorno_invalido_do_servico_nao_autoriza_repeticao(monkeypatch, contexto, documentos):
    executar = AsyncMock(return_value=None)
    monkeypatch.setattr(executor, "executar_servico", executar)

    async def verificar():
        await preparar_operacao(contexto, "feedback", "mensagem", {"comentario": "Teste"})
        for _ in range(2):
            resultado = await executor.executar_operacoes(estado_aprovado(contexto), SimpleNamespace(context=contexto))
            assert "pode ter ocorrido" in resultado["resposta_final"]

    asyncio.run(verificar())
    executar.assert_awaited_once()


def test_falha_ao_preparar_nao_registra_operacao_para_execucao(monkeypatch, contexto):
    monkeypatch.setattr(persistencia, "preparar", AsyncMock(side_effect=ConnectionError()))
    with pytest.raises(ConnectionError):
        asyncio.run(preparar_operacao(contexto, "feedback", "mensagem", {"comentario": "Teste"}))
    assert contexto["operacoes_pendentes"] == []


def test_update_confirmado_nao_vira_recusa_se_releitura_nao_traz_detalhes(monkeypatch, contexto):
    servico = import_module("app.services.ajuda_geral.edicoes")
    conexao = SimpleNamespace(execute=AsyncMock(side_effect=[
        SimpleNamespace(first=lambda: (10,)),
        SimpleNamespace(mappings=lambda: SimpleNamespace(first=lambda: None)),
    ]))

    @asynccontextmanager
    async def transacao():
        yield conexao

    monkeypatch.setattr(servico, "obter_motor", lambda perfil: SimpleNamespace(begin=transacao))
    monkeypatch.setattr(servico, "obter_unidade_id", AsyncMock(return_value=1))
    resultado = asyncio.run(servico.alterar_solicitacao(contexto["usuario"], 10, "titulo", "Novo"))
    assert resultado == {"id": 10}
