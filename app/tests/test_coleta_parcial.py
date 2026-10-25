"""Continuidade de cadastros incompletos e anexos recebidos antes da proposta."""

import asyncio
from contextlib import asynccontextmanager
from importlib import import_module
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.agentsResult import SolicitacaoOcorrenciaResultado
from app.core.propostas import avaliar_confirmacao
from app.graph import nos


@pytest.mark.parametrize("tipo", ["ocorrencia", "solicitacao"])
def test_foto_antiga_e_relato_continuam_ate_proposta_completa(monkeypatch, tipo):
    modulo = import_module("app.memory.persistencia.rascunho_solicitacao")
    campo = f"{tipo}_pendente"
    outro = "solicitacao_pendente" if tipo == "ocorrencia" else "ocorrencia_pendente"
    documento = {campo: None, outro: None, "anexos_pendentes": ["https://exemplo.com/foto.jpg"]}
    colecao = SimpleNamespace(
        find_one=AsyncMock(side_effect=lambda *_args, **_kwargs: documento.copy()),
        update_one=AsyncMock(return_value=SimpleNamespace(matched_count=1)),
    )

    @asynccontextmanager
    async def cliente():
        yield {modulo.MONGO_BANCO_DADOS: {modulo.MONGO_COLECAO_SESSOES: colecao}}

    monkeypatch.setattr(modulo, "abrir_cliente_mongo", cliente)
    monkeypatch.setattr(modulo, "obter_documento_sessao_id", AsyncMock(return_value="documento"))

    async def fluxo():
        primeiro = await modulo.registrar_coleta_parcial(
            "sessao", 7, tipo=tipo, turno_id="turno-1", relato="Reparei o equipamento no térreo",
        )
        assert primeiro["status_fluxo"] == "coletando_dados"
        assert primeiro["imagens"] == ["https://exemplo.com/foto.jpg"]
        assert colecao.update_one.await_args.args[1]["$unset"] == {"anexos_pendentes": ""}
        documento[campo] = primeiro
        documento["anexos_pendentes"] = []

        segundo = await modulo.registrar_coleta_parcial(
            "sessao", 7, tipo=tipo, turno_id="turno-2",
            relato="Somente entreguei ao Helpdesk; não sei o que fizeram depois",
        )
        assert segundo["id"] == primeiro["id"]
        assert segundo["versao"] == primeiro["versao"]
        assert [item["turno_id"] for item in segundo["relatos"]] == ["turno-1", "turno-2"]
        documento[campo] = segundo
        dados = {"titulo": "Entrega ao Helpdesk", "descricao_local": "Sala de matemática"}
        proposta = await modulo.salvar_rascunho_solicitacao(
            "sessao", 7, dados, tipo=tipo, turno_id="turno-2",
        )
        assert proposta["status_fluxo"] == "aguardando_confirmacao"
        assert proposta["imagens"] == primeiro["imagens"]
        assert proposta["id"] == primeiro["id"]
        assert proposta["versao"] == 2
        assert proposta["relatos"] == segundo["relatos"]
        assert avaliar_confirmacao(primeiro, {"turno_id": "turno-2", "mensagem_atual": "Pode registrar"})

    asyncio.run(fluxo())


def test_especialista_recebe_coleta_e_foto_sem_novo_pedido(monkeypatch):
    usuario = SimpleNamespace(usuario_id=7)
    relato = "Apenas entreguei o ar condicionado ao Helpdesk"
    contexto = {"session_id": "sessao", "usuario": usuario, "turno_id": "turno-2",
                "mensagem_atual": relato, "imagens": []}
    parcial = {"id": "rascunho", "tipo": "ocorrencia", "versao": 1,
               "status_fluxo": "coletando_dados", "dados": {}, "imagens": ["foto"],
               "relatos": [{"turno_id": "turno-1", "texto": "Apaguei o fogo"},
                           {"turno_id": "turno-2", "texto": relato}]}
    registrar = AsyncMock(return_value=parcial)
    monkeypatch.setattr(nos, "registrar_coleta_parcial", registrar)
    monkeypatch.setattr(nos, "obter_rascunho_solicitacao", AsyncMock(return_value=parcial))

    async def executar(_agente, estado, _contexto, _formato):
        textos = [msg.content for msg in estado["messages"] if isinstance(msg, SystemMessage)]
        assert any('"quantidade_imagens": 1' in texto for texto in textos)
        assert any(relato in texto for texto in textos)
        return {"structured_response": SolicitacaoOcorrenciaResultado(
            agente="solicitacao", resposta="Preciso confirmar o local.", status="AGUARDANDO_INFORMACAO",
        )}, []

    monkeypatch.setattr(nos, "executar_com_evidencias", executar)
    estado = {"perfil": "tecnico", "intencao": "ocorrencia", "cadastro_em_andamento": True,
              "messages": [HumanMessage(content=relato)], "evidencias": []}
    resposta = asyncio.run(nos.executar_solicitacao(estado, SimpleNamespace(context=contexto)))
    assert resposta["erro"] is None
    registrar.assert_awaited_once_with("sessao", 7, tipo="ocorrencia", turno_id="turno-2", relato=relato)


def test_consulta_de_ocorrencias_nao_inicia_rascunho(monkeypatch):
    registrar = AsyncMock()
    anexar = AsyncMock()
    monkeypatch.setattr(nos, "registrar_coleta_parcial", registrar)
    monkeypatch.setattr(nos, "adicionar_imagens_sessao", anexar)
    monkeypatch.setattr(nos, "obter_rascunho_solicitacao", AsyncMock(return_value=None))

    async def executar(_agente, _estado, _contexto, _formato):
        return {"structured_response": SolicitacaoOcorrenciaResultado(
            agente="solicitacao", resposta="Encontrei os registros.", status="SUCESSO",
        )}, []

    monkeypatch.setattr(nos, "executar_com_evidencias", executar)
    contexto = {"session_id": "sessao", "usuario": SimpleNamespace(usuario_id=7),
                "turno_id": "turno", "mensagem_atual": "Liste minhas ocorrências", "imagens": ["foto"]}
    estado = {"perfil": "tecnico", "intencao": "ocorrencia", "cadastro_em_andamento": False,
              "messages": [HumanMessage(content="Liste minhas ocorrências")], "evidencias": []}
    resposta = asyncio.run(nos.executar_solicitacao(estado, SimpleNamespace(context=contexto)))
    assert resposta["erro"] is None
    registrar.assert_not_awaited()
    anexar.assert_not_awaited()


def test_primeira_mensagem_com_foto_anexa_ao_rascunho_parcial(monkeypatch):
    registrar = AsyncMock(return_value={"status_fluxo": "coletando_dados"})
    anexar = AsyncMock()
    monkeypatch.setattr(nos, "registrar_coleta_parcial", registrar)
    monkeypatch.setattr(nos, "adicionar_imagens_sessao", anexar)
    monkeypatch.setattr(nos, "obter_rascunho_solicitacao", AsyncMock(return_value={
        "status_fluxo": "coletando_dados", "dados": {}, "imagens": ["https://exemplo.com/foto.jpg"],
        "relatos": [{"turno_id": "turno-1", "texto": "Apaguei o fogo"}],
    }))

    async def executar(_agente, estado, _contexto, _formato):
        assert any('"quantidade_imagens": 1' in msg.content for msg in estado["messages"]
                   if isinstance(msg, SystemMessage))
        return {"structured_response": SolicitacaoOcorrenciaResultado(
            agente="solicitacao", resposta="Em qual sala foi feito o serviço?",
            status="AGUARDANDO_INFORMACAO",
        )}, []

    monkeypatch.setattr(nos, "executar_com_evidencias", executar)
    contexto = {"session_id": "sessao", "usuario": SimpleNamespace(usuario_id=7),
                "turno_id": "turno-1", "mensagem_atual": "Apaguei o fogo",
                "imagens": ["https://exemplo.com/foto.jpg"]}
    estado = {"perfil": "tecnico", "intencao": "ocorrencia", "cadastro_em_andamento": True,
              "messages": [HumanMessage(content="Apaguei o fogo")], "evidencias": []}
    resultado = asyncio.run(nos.executar_solicitacao(estado, SimpleNamespace(context=contexto)))
    assert resultado["erro"] is None
    registrar.assert_awaited_once()
    anexar.assert_awaited_once_with("sessao", 7, ["https://exemplo.com/foto.jpg"], tipo="ocorrencia")


def test_coleta_parcial_nao_envia_cadastro(monkeypatch):
    modulo = import_module("app.tools.ocorrencias.criarOcorrencia")
    parcial = {"status_fluxo": "coletando_dados", "dados": {}, "imagens": ["foto"]}
    monkeypatch.setattr(modulo, "_contexto", lambda _: ({}, SimpleNamespace(
        tipo_acesso="tecnico", usuario_id=7,
    ), "sessao"))
    monkeypatch.setattr(modulo, "obter_rascunho_solicitacao", AsyncMock(return_value=parcial))
    enviar = AsyncMock()
    monkeypatch.setattr(modulo, "adicionar_ocorrencia", enviar)
    resultado = asyncio.run(modulo.criar_ocorrencia.coroutine(None))
    assert resultado["status"] == "RASCUNHO_INDISPONIVEL"
    enviar.assert_not_awaited()
