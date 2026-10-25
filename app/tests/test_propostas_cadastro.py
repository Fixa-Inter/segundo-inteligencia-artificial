import asyncio
import json
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from importlib import import_module
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from app.core.propostas import avaliar_confirmacao, campos_pendentes, metadados_proposta, resumo_confirmacao


def dados(tipo):
    comuns = {"local_endereco_id": 2, "categoria_equipamento_id": 3, "titulo": "Ventilador",
              "descricao_local": "Sala 2"}
    if tipo == "solicitacao":
        return {**comuns, "descricao_problema": "Não liga"}
    return {**comuns, "descricao_ocorrencia": "Troca do motor", "categoria_problema_id": "MECANICA", "prioridade": "BAIXA"}


def proposta(tipo="solicitacao"):
    registro = dados(tipo)
    return {"id": "rascunho", "versao": 1, "tipo": tipo, "turno_id": "proposta",
            "turno_apresentacao": "resposta", "versao_apresentada": 1, "dados_apresentados": registro.copy(),
            "dados": registro, "dados_confirmados": {}, "confirmado": False,
            "status_fluxo": "aguardando_confirmacao", "imagens": ["https://exemplo.com/foto.jpg"],
            "rotulos": {"local_endereco_id": "Sala 2", "categoria_equipamento_id": "Ventiladores"}}


def contexto(mensagem="Sim"):
    return {"turno_id": "confirmacao", "mensagem_atual": mensagem, "imagens": []}


@pytest.mark.parametrize("mudanca", [
    {"turno_id": "confirmacao"}, {"versao": 2}, {"turno_apresentacao": None},
    {"dados_apresentados": {"titulo": "Outro"}}, {"pausado": True},
])
def test_proposta_invalida_nao_recebe_aceite(mudanca):
    registro = {**proposta(), **mudanca}
    assert avaliar_confirmacao(registro, contexto())["status"] == "CONFIRMACAO_NECESSARIA"


def test_foto_posterior_preserva_aceite_sem_nova_confirmacao():
    registro = proposta()
    registro.update(confirmado=True, dados_confirmados=registro["dados"].copy(), status_fluxo="aguardando_imagem")
    assert avaliar_confirmacao(registro, {**contexto("Segue a foto"), "imagens": ["foto"]}) is None
    assert avaliar_confirmacao(registro, contexto("Pode alterar?")) is not None
    assert avaliar_confirmacao(registro, contexto("Conte uma piada")) is not None


def test_resumo_alteracao_mostra_somente_campo_pendente():
    registro = proposta()
    registro["dados_confirmados"] = registro["dados"].copy()
    registro["dados"]["descricao_local"] = "Sala 3"
    assert campos_pendentes(registro) == ["descricao_local"]
    resumo = resumo_confirmacao(registro)
    assert "somente o que mudou" in resumo
    assert "Sala 3" in resumo
    assert "Categoria do equipamento" not in resumo


@pytest.mark.parametrize("tipo", ["solicitacao", "ocorrencia"])
@pytest.mark.parametrize("mensagem", ["Sim", "Pode registrar", "Pode registrar?", "Sim, mas mude o local", "Confirmo o local"])
def test_cadastro_respeita_aceite_e_versao(monkeypatch, tipo, mensagem):
    modulo = import_module(f"app.tools.{('solicitacoes.criarSolicitacao' if tipo == 'solicitacao' else 'ocorrencias.criarOcorrencia')}")
    registro = proposta(tipo)
    usuario = SimpleNamespace(tipo_acesso="tecnico", usuario_id=7, access_token="teste")
    monkeypatch.setattr(modulo, "_contexto", lambda _: (contexto(mensagem), usuario, "sessao"))
    monkeypatch.setattr(modulo, "obter_rascunho_solicitacao", AsyncMock(return_value=registro))
    atualizar = AsyncMock(return_value=True)
    monkeypatch.setattr(modulo, "atualizar_rascunho_solicitacao", atualizar)
    monkeypatch.setattr(modulo, "obter_unidade_id", AsyncMock(return_value=1))
    monkeypatch.setattr(modulo, "validar_selecao", AsyncMock())

    @asynccontextmanager
    async def cliente():
        yield object()

    monkeypatch.setattr(modulo, "abrir_cliente_qdrant", cliente)
    cadastrar = AsyncMock(return_value={"status": "SUCESSO", "problema_id": 4, "ocorrencia_id": 4})
    monkeypatch.setattr(modulo, f"adicionar_{tipo}", cadastrar)
    resultado = asyncio.run(getattr(modulo, f"criar_{tipo}").coroutine(None))
    if mensagem.endswith("?") or "mas" in mensagem:
        assert resultado["status"] == "CONFIRMACAO_NECESSARIA"
        cadastrar.assert_not_awaited()
        atualizar.assert_not_awaited()
    elif mensagem == "Confirmo o local":
        assert resultado["status"] == "CONFIRMACAO_PARCIAL"
        cadastrar.assert_not_awaited()
        aceitos = atualizar.await_args.args[2]["dados_confirmados"]
        assert set(aceitos) == {"local_endereco_id", "descricao_local"}
        assert "Título" in resultado["proposta"]["resumo_confirmacao"]
        assert "Detalhes do local" not in resultado["proposta"]["resumo_confirmacao"]
    else:
        assert resultado["status"] == "SUCESSO"
        cadastrar.assert_awaited_once()
        assert all(chamada.kwargs["rascunho_id"] == "rascunho" and chamada.kwargs["versao"] == 1
                   for chamada in atualizar.await_args_list)


@pytest.mark.parametrize("tipo", ["solicitacao", "ocorrencia"])
def test_versao_criada_mesmo_turno_nao_chama_backend(monkeypatch, tipo):
    modulo = import_module(f"app.tools.{('solicitacoes.criarSolicitacao' if tipo == 'solicitacao' else 'ocorrencias.criarOcorrencia')}")
    registro = proposta(tipo)
    registro["turno_id"] = "confirmacao"
    monkeypatch.setattr(modulo, "_contexto", lambda _: (contexto(), SimpleNamespace(tipo_acesso="tecnico", usuario_id=7), "sessao"))
    monkeypatch.setattr(modulo, "obter_rascunho_solicitacao", AsyncMock(return_value=registro))
    cadastrar = AsyncMock()
    monkeypatch.setattr(modulo, f"adicionar_{tipo}", cadastrar)
    resultado = asyncio.run(getattr(modulo, f"criar_{tipo}").coroutine(None))
    assert resultado["status"] == "CONFIRMACAO_NECESSARIA"
    cadastrar.assert_not_awaited()


def test_atualizar_rascunho_preserva_aceite_campos_inalterados(monkeypatch):
    modulo = import_module("app.memory.persistencia.rascunho_solicitacao")
    anterior = proposta()
    anterior["dados_confirmados"] = anterior["dados"].copy()
    documento = {"solicitacao_pendente": anterior, "anexos_pendentes": []}
    colecao = SimpleNamespace(find_one=AsyncMock(return_value=documento),
                             update_one=AsyncMock(return_value=SimpleNamespace(matched_count=1)))

    @asynccontextmanager
    async def cliente():
        yield {modulo.MONGO_BANCO_DADOS: {modulo.MONGO_COLECAO_SESSOES: colecao}}

    monkeypatch.setattr(modulo, "abrir_cliente_mongo", cliente)
    monkeypatch.setattr(modulo, "obter_documento_sessao_id", AsyncMock(return_value="documento"))
    novos_dados = {**anterior["dados"], "descricao_local": "Sala 3"}
    novo = asyncio.run(modulo.salvar_rascunho_solicitacao("sessao", 7, novos_dados, turno_id="correcao"))
    assert novo["versao"] == 2
    assert novo["turno_id"] == "correcao"
    assert novo["dados_confirmados"]["titulo"] == "Ventilador"
    assert "descricao_local" not in novo["dados_confirmados"]
    assert campos_pendentes(novo) == ["descricao_local"]
    assert "turno_apresentacao" not in novo
    assert colecao.update_one.await_args.args[0]["solicitacao_pendente"] == anterior


def test_resumo_conferido_juiz_antes_de_ser_marcado_apresentado(monkeypatch):
    from langchain_core.messages import HumanMessage
    from app.agents.juiz import julgar_resposta
    from app.graph.nos import validar_saida

    resumo = metadados_proposta(proposta())
    estado = {"perfil": "solicitante", "messages": [HumanMessage(content="Ventilador quebrado")],
              "resposta_especialista": "Confira os detalhes.", "evidencias": [json.dumps({
                  "ferramenta": "salvar_rascunho_solicitacao", "status_execucao": "success",
                  "resultado": {"status": "RASCUNHO_SALVO", "proposta": resumo},
              })]}
    julgador = AsyncMock(return_value={"model": "jev-teste", "answers": {
        "veredito": {"type": "choice", "choice": "aprovado", "confidence": 0.95},
        "motivo": {"type": "choice", "choice": "nenhum", "confidence": 0.95},
        "afirmacao_sem_suporte": {"type": "noul", "noul": 0.05},
        "correcao_textual": {"type": "noul", "noul": 0.05},
        "risco_grave": {"type": "noul", "noul": 0.05},
    }})
    monkeypatch.setattr(import_module("app.agents.juiz"), "consultar_jev", julgador)
    estado.update(asyncio.run(julgar_resposta(estado)))
    assert resumo["resumo_confirmacao"] in julgador.await_args.args[0]["resposta_candidata"]
    assert validar_saida(estado)["propostas_apresentadas"] == [resumo]
    estado["veredito"] = "bloqueado"
    assert not validar_saida(estado).get("propostas_apresentadas")


def test_contexto_temporal_converte_dia_timezone():
    from app.agents.prompts.reutilizaveis import construir_contexto_temporal
    texto = construir_contexto_temporal(datetime(2026, 10, 16, 1, 30, tzinfo=timezone.utc))
    assert "2026-10-15T22:30:00-03:00" in texto
    assert "America/Sao_Paulo" in texto


def test_aceite_local_confirma_somente_local_e_preserva_restante():
    registro = proposta()
    resultado = avaliar_confirmacao(registro, contexto("Confirmo o local"))
    assert resultado["status"] == "CONFIRMACAO_PARCIAL"
    assert set(resultado["campos_confirmados"]) == {"local_endereco_id", "descricao_local"}
    registro["dados_confirmados"] = {campo: valor for campo, valor in registro["dados"].items()
                                    if campo != "descricao_local"}
    assert avaliar_confirmacao(registro, contexto("O local está correto")) is None


def test_aceite_foto_nao_confirma_dados_e_categoria_ambigua_esclarecida():
    assert avaliar_confirmacao(proposta(), contexto("Confirmo a foto"))["status"] == "CONFIRMACAO_NECESSARIA"
    assert avaliar_confirmacao(proposta("ocorrencia"), contexto("Confirmo a categoria"))["status"] == "CONFIRMACAO_NECESSARIA"


@pytest.mark.parametrize("falhar_resposta,marcada", [(False, True), (False, False), (True, True)])
def test_apresentacao_registrada_somente_depois_resposta_persistida(monkeypatch, falhar_resposta, marcada):
    from app.graph import executor
    eventos = []
    metadados = metadados_proposta(proposta())
    resultado_grafo = {"resposta_final": metadados["resumo_confirmacao"], "propostas_apresentadas": [metadados]}
    monkeypatch.setattr(executor, "grafo", SimpleNamespace(
        get_state=lambda _: SimpleNamespace(values={}), ainvoke=AsyncMock(return_value=resultado_grafo),
    ))
    monkeypatch.setattr(executor, "obter_documento_sessao_id", AsyncMock(return_value="documento"))
    monkeypatch.setattr(executor, "recuperar_mensagens", AsyncMock(return_value=[]))
    monkeypatch.setattr(executor, "obter_rascunho_solicitacao", AsyncMock(return_value=None))
    monkeypatch.setattr(executor, "obter_acao", AsyncMock(return_value=None))

    async def salvar(sessao, papel, *args, **kwargs):
        eventos.append(papel)
        if papel == "assistant" and falhar_resposta:
            raise RuntimeError("Falha ao persistir a resposta")

    async def marcar(*args, **kwargs):
        eventos.append("apresentacao")
        assert eventos[-2] == "assistant"
        assert kwargs["rascunho_id"] == metadados["proposta_id"]
        assert kwargs["versao"] == metadados["versao"]
        return marcada

    monkeypatch.setattr(executor, "salvar_mensagem", salvar)
    atualizar = AsyncMock(side_effect=marcar)
    monkeypatch.setattr(executor, "atualizar_rascunho_solicitacao", atualizar)
    chamada = executor.executar_grafo("Ventilador quebrado", SimpleNamespace(usuario_id=7, tipo_acesso="tecnico"), "sessao")
    if falhar_resposta:
        with pytest.raises(RuntimeError):
            asyncio.run(chamada)
        atualizar.assert_not_awaited()
    else:
        resultado = asyncio.run(chamada)
        assert eventos == ["human", "assistant", "apresentacao"]
        assert resultado["confirmacao"] == ("sim" if marcada else "nao")


@pytest.mark.parametrize("pausado,mostrar_resumo,esperado", [
    (False, True, "sim"), (True, True, "nao"), (False, False, "nao"),
])
def test_reapresentacao_da_proposta_controla_botao_de_confirmacao(
    monkeypatch, pausado, mostrar_resumo, esperado,
):
    from app.graph import executor

    rascunho = {**proposta("ocorrencia"), "pausado": pausado}
    texto = resumo_confirmacao(rascunho) if mostrar_resumo else "A ocorrência permanece pendente."
    monkeypatch.setattr(executor, "grafo", SimpleNamespace(
        get_state=lambda _: SimpleNamespace(values={}),
        ainvoke=AsyncMock(return_value={
            "intencao": "ocorrencia", "ocorrencia_pendente": rascunho,
            "resposta_final": texto, "propostas_apresentadas": [],
        }),
    ))
    monkeypatch.setattr(executor, "obter_documento_sessao_id", AsyncMock(return_value="documento"))
    monkeypatch.setattr(executor, "recuperar_mensagens", AsyncMock(return_value=[]))
    monkeypatch.setattr(executor, "obter_rascunho_solicitacao", AsyncMock(return_value=None))
    monkeypatch.setattr(executor, "obter_acao", AsyncMock(return_value=None))
    monkeypatch.setattr(executor, "salvar_mensagem", AsyncMock())
    monkeypatch.setattr(executor, "atualizar_rascunho_solicitacao", AsyncMock())

    resultado = asyncio.run(executor.executar_grafo(
        "Voltei à ocorrência do notebook", SimpleNamespace(usuario_id=7, tipo_acesso="tecnico"),
        "sessao",
    ))
    assert resultado["confirmacao"] == esperado


def test_referencia_temporal_renovada_entre_invocacoes(monkeypatch):
    from langchain_core.messages import SystemMessage
    from app.graph.evidencias import executar_com_evidencias
    modulo = import_module("app.agents.prompts.reutilizaveis.gerais.contexto_temporal")
    monkeypatch.setattr(modulo, "agora_local", Mock(side_effect=[
        datetime(2026, 10, 15, 23, 59, tzinfo=modulo.FUSO_HORARIO),
        datetime(2026, 10, 16, 0, 1, tzinfo=modulo.FUSO_HORARIO),
    ]))
    agente = SimpleNamespace(ainvoke=AsyncMock(return_value={"messages": []}))
    for _ in range(2):
        asyncio.run(executar_com_evidencias(agente, {"messages": []}, {}, SimpleNamespace(__name__="Formato")))
    referencias = [chamada.args[0]["messages"][0] for chamada in agente.ainvoke.await_args_list]
    assert all(isinstance(mensagem, SystemMessage) for mensagem in referencias)
    assert "2026-10-15" in referencias[0].content
    assert "2026-10-16" in referencias[1].content


@pytest.mark.parametrize("tipo", ["solicitacao", "ocorrencia"])
@pytest.mark.parametrize("falha_confirmacao", [True, False])
def test_conflito_versao_impede_envio(monkeypatch, tipo, falha_confirmacao):
    modulo = import_module(f"app.tools.{('solicitacoes.criarSolicitacao' if tipo == 'solicitacao' else 'ocorrencias.criarOcorrencia')}")
    usuario = SimpleNamespace(tipo_acesso="tecnico", usuario_id=7, access_token="teste")
    monkeypatch.setattr(modulo, "_contexto", lambda _: (contexto(), usuario, "sessao"))
    monkeypatch.setattr(modulo, "obter_rascunho_solicitacao", AsyncMock(return_value=proposta(tipo)))
    monkeypatch.setattr(modulo, "atualizar_rascunho_solicitacao", AsyncMock(side_effect=[False] if falha_confirmacao else [True, False]))
    monkeypatch.setattr(modulo, "obter_unidade_id", AsyncMock(return_value=1))
    monkeypatch.setattr(modulo, "validar_selecao", AsyncMock())

    @asynccontextmanager
    async def cliente():
        yield object()

    monkeypatch.setattr(modulo, "abrir_cliente_qdrant", cliente)
    cadastrar = AsyncMock()
    monkeypatch.setattr(modulo, f"adicionar_{tipo}", cadastrar)
    resultado = asyncio.run(getattr(modulo, f"criar_{tipo}").coroutine(None))
    assert resultado["status"] == "RESULTADO_INDETERMINADO"
    cadastrar.assert_not_awaited()
