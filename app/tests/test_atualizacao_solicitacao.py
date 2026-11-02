"""Atualizações próprias: duas conferências, fotos e execução aprovada."""

import asyncio
import json
from contextlib import asynccontextmanager
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.agents import ajuda_geral, solicitacoes
from app.schemas import UsuarioContexto
from app.core.propostas import metadados_proposta
from app.services.operacoes import dados_atualizacao, aprovacao_operacoes
from app.services.solicitacoes import atualizarSolicitacao as servico
from app.tools.solicitacoes import atualizarSolicitacao as ferramentas
from app.graph import operacoes, propostas
from app.tests.test_operacoes_aprovadas import documentos  # fixture de operações Mongo com compare-and-set


def registro():
    return {"id": 12, "titulo": "Torneira com vazamento", "descricao_problema": "Pinga mesmo fechada",
            "descricao_local": "Perto da entrada", "local_unidade_id": 2, "categoria_equipamento_id": 3,
            "local": "Sala 2", "categoria_equipamento": "Torneiras", "status": 0,
            "fotos": [{"id": 9, "url": "https://example.com/antiga.jpg"}]}


@pytest.mark.parametrize("perfil", ["solicitante", "tecnico", "gestor", "administrador"])
def test_todos_perfis_recebem_atualizacao_e_listagem_feedbacks(monkeypatch, perfil):
    from app.tools.feedback.listarFeedbacks import listar_meus_feedbacks
    monkeypatch.setattr(ajuda_geral, "create_agent", lambda **kwargs: kwargs)
    monkeypatch.setattr(solicitacoes, "create_agent", lambda **kwargs: kwargs)
    consulta = ajuda_geral.criar_agente_ajuda_geral(object(), "teste", perfil=perfil)
    cadastro = solicitacoes.criar_agente_solicitacoes(object(), "teste", **{
        "gestor" if perfil == "administrador" else perfil: True,
    })
    assert listar_meus_feedbacks in consulta["tools"]
    for agente in (consulta, cadastro):
        assert ferramentas.buscar_solicitacoes_para_atualizar in agente["tools"]
        assert ferramentas.atualizar_solicitacao in agente["tools"]


@pytest.fixture
def fluxo(monkeypatch):
    atual = {"id": "rascunho", "tipo": "solicitacao", "operacao": "atualizar", "versao": 1,
             "status_fluxo": "coletando_dados", "dados": {}, "imagens": [], "pausado": False,
             "turno_id": "busca", "dados_confirmados": {}}
    contexto = {"usuario": UsuarioContexto.model_construct(usuario_id=7, tipo_acesso="solicitante", access_token="teste"),
                "session_id": "sessao", "turno_id": "busca", "mensagem_atual": "Quero alterar a torneira",
                "imagens": [], "operacoes_pendentes": [], "resultados_operacoes": []}

    async def obter(*args, **kwargs):
        return deepcopy(atual)

    async def salvar(sessao, usuario_id, campos, **controle):
        assert sessao == "sessao" and usuario_id == 7
        if (controle.get("rascunho_id") != atual["id"] or controle.get("versao") != atual["versao"]
                or atual["status_fluxo"] not in controle.get("status_esperados", [])):
            return False
        atual.update(deepcopy(campos))
        return True

    monkeypatch.setattr(ferramentas, "obter_rascunho_solicitacao", obter)
    monkeypatch.setattr(ferramentas, "atualizar_rascunho_solicitacao", salvar)
    monkeypatch.setattr(ferramentas, "registrar_coleta_parcial", obter)
    monkeypatch.setattr(servico, "buscar_proprias_pendentes", AsyncMock(return_value=[registro()]))
    monkeypatch.setattr(servico, "consultar_propria_pendente", AsyncMock(return_value=registro()))
    monkeypatch.setattr(servico, "localizar_opcao", AsyncMock(return_value={"id": 4, "nome": "Sala 4"}))
    gravar = AsyncMock(return_value={"id": 12})
    monkeypatch.setattr(servico, "atualizar_propria_pendente", gravar)
    return SimpleNamespace(atual=atual, contexto=contexto, runtime=SimpleNamespace(context=contexto), gravar=gravar)


def turno(fluxo, mensagem, imagens=None):
    fluxo.contexto["turno_id"] += "-seguinte"
    fluxo.contexto["mensagem_atual"] = mensagem
    fluxo.contexto["imagens"] = imagens or []


async def selecionar(fluxo, **alteracoes):
    await ferramentas.buscar_solicitacoes_para_atualizar.coroutine("torneira", fluxo.runtime)
    return await ferramentas.atualizar_solicitacao.coroutine(fluxo.runtime, problema_id=12, **alteracoes)


def apresentar(fluxo, resposta):
    proposta = resposta["proposta"]
    if proposta["etapa"] == "selecao":
        fluxo.atual.update(turno_selecao_apresentada=fluxo.contexto["turno_id"],
                           versao_selecao_apresentada=proposta["versao"])
    else:
        fluxo.atual.update(turno_apresentacao=fluxo.contexto["turno_id"],
                           atualizacao_apresentada=deepcopy(proposta["atualizacao"]))


def test_selecao_tem_titulo_e_descricao_consecutivos_e_passa_pelo_montador(fluxo):
    resposta = asyncio.run(selecionar(fluxo, descricao_problema="Não veda"))
    resumo = resposta["proposta"]["resumo_confirmacao"]
    assert resumo == "A solicitação que você quer alterar é esta?\n\n**Torneira com vazamento**  \nPinga mesmo fechada"
    assert "Não veda" not in resumo and "Sala 2" not in resumo
    evidencia = json.dumps({"ferramenta": "atualizar_solicitacao", "status_execucao": "success", "resultado": resposta})
    assert propostas.preparar_resposta("Encontrei a solicitação.", {"evidencias": [evidencia]})[2].endswith(resumo)
    fluxo.gravar.assert_not_awaited()


@pytest.mark.parametrize("aceite", ["Sim", "Pode atualizar", "É essa", "Essa mesma"])
def test_aceite_da_selecao_nunca_prepara_operacao_e_mostra_resultado_final(fluxo, aceite):
    selecao = asyncio.run(selecionar(fluxo, titulo="Torneira sem vedação", descricao_local="Ao lado da porta"))
    apresentar(fluxo, selecao)
    turno(fluxo, aceite)
    final = asyncio.run(ferramentas.atualizar_solicitacao.coroutine(fluxo.runtime))
    assert final["proposta"]["etapa"] == "final"
    assert "Torneira sem vedação" in final["proposta"]["resumo_confirmacao"]
    assert "Ao lado da porta" in final["proposta"]["resumo_confirmacao"]
    assert "Sala 2" in final["proposta"]["resumo_confirmacao"]
    assert fluxo.contexto["operacoes_pendentes"] == []
    fluxo.gravar.assert_not_awaited()


@pytest.mark.parametrize("mensagem,acao", [("Sim, adicione as fotos", "adicionar"),
                                         ("É essa, substitua todas as fotos", "substituir")])
def test_aceite_de_identificacao_com_escolha_de_fotos_so_mostra_proposta_final(fluxo, mensagem, acao):
    fluxo.contexto["imagens"] = ["https://example.com/nova.jpg"]
    selecao = asyncio.run(selecionar(fluxo, titulo="Novo título"))
    apresentar(fluxo, selecao)
    turno(fluxo, mensagem)
    final = asyncio.run(ferramentas.atualizar_solicitacao.coroutine(fluxo.runtime, acao_fotos=acao))
    assert final["proposta"]["etapa"] == "final"
    assert final["proposta"]["atualizacao"]["acao_fotos"] == acao
    assert fluxo.contexto["operacoes_pendentes"] == []
    fluxo.gravar.assert_not_awaited()


@pytest.mark.parametrize("apresentada,novo_turno", [(False, True), (True, False)])
def test_selecao_exige_apresentacao_persistida_em_turno_anterior(fluxo, apresentada, novo_turno):
    selecao = asyncio.run(selecionar(fluxo, titulo="Novo título"))
    if apresentada:
        apresentar(fluxo, selecao)
    if novo_turno:
        turno(fluxo, "Sim")
    else:
        fluxo.contexto["mensagem_atual"] = "Sim"
    assert asyncio.run(ferramentas.atualizar_solicitacao.coroutine(fluxo.runtime))["proposta"]["etapa"] == "selecao"
    assert not fluxo.atual.get("selecao_confirmada")


def test_fotos_da_mensagem_inicial_sao_preservadas_e_escolha_nao_pode_ser_inventada(fluxo):
    fluxo.contexto["imagens"] = ["https://example.com/nova.jpg"]
    selecao = asyncio.run(selecionar(fluxo, titulo="Novo título", acao_fotos="substituir"))
    apresentar(fluxo, selecao)
    turno(fluxo, "Sim")
    resposta = asyncio.run(ferramentas.atualizar_solicitacao.coroutine(fluxo.runtime, acao_fotos="substituir"))
    assert resposta["status"] == "AGUARDANDO_INFORMACAO"
    assert fluxo.atual["imagens"] == ["https://example.com/nova.jpg"]
    turno(fluxo, "Quero substituir todas as fotos")
    final = asyncio.run(ferramentas.atualizar_solicitacao.coroutine(fluxo.runtime, acao_fotos="substituir"))
    assert final["proposta"]["atualizacao"]["acao_fotos"] == "substituir"
    assert "substituir todas" in final["proposta"]["resumo_confirmacao"]


@pytest.mark.parametrize("mensagem", ["Não quero substituir as fotos", "Você vai substituir todas?", "Talvez substituir depois"])
def test_pergunta_ou_negacao_nao_autoriza_substituir_fotos(fluxo, mensagem):
    fluxo.contexto["imagens"] = ["https://example.com/nova.jpg"]
    selecao = asyncio.run(selecionar(fluxo, titulo="Novo título"))
    apresentar(fluxo, selecao)
    turno(fluxo, "Sim")
    asyncio.run(ferramentas.atualizar_solicitacao.coroutine(fluxo.runtime))
    turno(fluxo, mensagem)
    retorno = asyncio.run(ferramentas.atualizar_solicitacao.coroutine(fluxo.runtime, acao_fotos="substituir"))
    assert retorno["status"] == "AGUARDANDO_INFORMACAO"
    assert fluxo.atual["acao_fotos"] is None
    fluxo.gravar.assert_not_awaited()


@pytest.mark.parametrize("incerto", [False, True])
def test_so_executor_aprovado_grava_e_segundo_aceite_nao_repete(fluxo, documentos, incerto):
    if incerto:
        fluxo.gravar.side_effect = TimeoutError("Resultado desconhecido")
    async def verificar():
        selecao = await selecionar(fluxo, titulo="Título atualizado")
        apresentar(fluxo, selecao)
        turno(fluxo, "Sim")
        final = await ferramentas.atualizar_solicitacao.coroutine(fluxo.runtime)
        apresentar(fluxo, final)
        turno(fluxo, "Pode atualizar")
        assert (await ferramentas.atualizar_solicitacao.coroutine(fluxo.runtime))["status"] == "OPERACAO_PREPARADA"
        fluxo.gravar.assert_not_awaited()
        estado = {"operacoes_pendentes": deepcopy(fluxo.contexto["operacoes_pendentes"]), "veredito": "bloqueado"}
        await operacoes.executar_operacoes(estado, fluxo.runtime)
        fluxo.gravar.assert_not_awaited()
        estado.update(veredito="aprovado", aprovacao_operacoes=aprovacao_operacoes(estado["operacoes_pendentes"], fluxo.contexto))
        resultado = await operacoes.executar_operacoes(estado, fluxo.runtime)
        assert resultado["resultados_operacoes"][0]["resultado"]["status"] == ("RESULTADO_INDETERMINADO" if incerto else "SUCESSO")
        await operacoes.executar_operacoes(estado, fluxo.runtime)
        turno(fluxo, "Sim")
        assert (await ferramentas.atualizar_solicitacao.coroutine(fluxo.runtime))["status"] == ("RESULTADO_INDETERMINADO" if incerto else "JA_CONCLUIDA")
        fluxo.gravar.assert_awaited_once()
    asyncio.run(verificar())


@pytest.mark.parametrize("campo", ["titulo", "imagens", "registro_id"])
def test_alteracao_depois_do_aceite_invalida_a_operacao(fluxo, campo):
    async def verificar():
        selecao = await selecionar(fluxo, titulo="Novo título")
        apresentar(fluxo, selecao)
        turno(fluxo, "Sim")
        final = await ferramentas.atualizar_solicitacao.coroutine(fluxo.runtime)
        apresentar(fluxo, final)
        turno(fluxo, "Pode atualizar")
        aprovado = deepcopy(dados_atualizacao(fluxo.atual))
        if campo == "titulo":
            fluxo.atual["alteracoes"]["titulo"] = "Outro título"
        elif campo == "imagens":
            fluxo.atual["imagens"] = ["https://example.com/outra.jpg"]
        else:
            fluxo.atual["registro_id"] = 999
        resultado = await ferramentas.processar_atualizacao(fluxo.runtime, operacao_aprovada=aprovado)
        assert resultado["status"] == "AGUARDANDO_CONFIRMACAO"
        fluxo.gravar.assert_not_awaited()
    asyncio.run(verificar())


def test_nao_seleciona_id_que_nao_veio_da_busca_propria(fluxo):
    asyncio.run(ferramentas.buscar_solicitacoes_para_atualizar.coroutine("torneira", fluxo.runtime))
    resposta = asyncio.run(ferramentas.atualizar_solicitacao.coroutine(fluxo.runtime, problema_id=99))
    assert resposta["status"] == "ERRO_VALIDACAO"
    servico.consultar_propria_pendente.assert_not_awaited()


def test_continuacao_preserva_operacao_de_atualizacao(fluxo):
    from app.graph.continuacoes import tratar_continuacao
    asyncio.run(selecionar(fluxo, titulo="Novo título"))
    estado = {"solicitacao_pendente": fluxo.atual}
    resultado = asyncio.run(tratar_continuacao(estado, fluxo.contexto, "Sim"))
    assert resultado["intencao"] == "solicitacao"
    assert resultado["operacao_solicitacao"] == "atualizar"


def test_nova_busca_descarta_selecao_e_conferencia_anteriores(fluxo):
    selecao = asyncio.run(selecionar(fluxo, titulo="Novo título"))
    apresentar(fluxo, selecao)
    turno(fluxo, "Sim")
    asyncio.run(ferramentas.atualizar_solicitacao.coroutine(fluxo.runtime))
    assert fluxo.atual["selecao_confirmada"] is True
    turno(fluxo, "Busque novamente a solicitação")
    asyncio.run(ferramentas.buscar_solicitacoes_para_atualizar.coroutine("torneira", fluxo.runtime))
    assert fluxo.atual["registro_id"] is None and fluxo.atual["selecao_confirmada"] is False
    assert asyncio.run(ferramentas.atualizar_solicitacao.coroutine(fluxo.runtime, problema_id=12))["proposta"]["etapa"] == "selecao"


def test_nova_foto_recebida_no_no_invalida_apresentacao_anterior(monkeypatch, fluxo):
    from app.memory.persistencia import rascunho_solicitacao as persistencia
    fluxo.atual.update(status_fluxo="aguardando_confirmacao", etapa="final", selecao_confirmada=True,
                        acao_fotos="manter")
    colecao = SimpleNamespace(find_one=AsyncMock(return_value={"solicitacao_pendente": deepcopy(fluxo.atual)}),
                             update_one=AsyncMock(return_value=SimpleNamespace(matched_count=1)))

    @asynccontextmanager
    async def abrir():
        yield {persistencia.MONGO_BANCO_DADOS: {persistencia.MONGO_COLECAO_SESSOES: colecao}}

    monkeypatch.setattr(persistencia, "abrir_cliente_mongo", abrir)
    monkeypatch.setattr(persistencia, "obter_documento_sessao_id", AsyncMock(return_value="documento"))
    asyncio.run(persistencia.adicionar_imagens_sessao("sessao", 7, ["https://example.com/nova.jpg"], tipo="solicitacao"))
    filtro, alteracao = colecao.update_one.await_args.args
    assert filtro["solicitacao_pendente.versao"] == fluxo.atual["versao"]
    assert alteracao["$set"]["solicitacao_pendente.versao"] == fluxo.atual["versao"] + 1
    assert alteracao["$set"]["solicitacao_pendente.status_fluxo"] == "coletando_dados"
    assert alteracao["$set"]["solicitacao_pendente.acao_fotos"] is None


def test_ferramenta_de_criacao_recusa_rascunho_de_atualizacao(fluxo):
    from app.tools.solicitacoes.criarSolicitacao import processar_solicitacao
    from unittest.mock import patch
    with patch("app.tools.solicitacoes.criarSolicitacao.obter_rascunho_solicitacao", AsyncMock(return_value=fluxo.atual)):
        resultado = asyncio.run(processar_solicitacao(fluxo.runtime))
    assert resultado["status"] == "ERRO_VALIDACAO"
    assert "atualização" in resultado["mensagem"]


def test_busca_vetorial_filtra_unidade_e_ids_proprios_pendentes(monkeypatch):
    from app.core import configuracao as cfg
    consultar = AsyncMock(return_value=[registro()])
    monkeypatch.setattr(servico, "executar_consulta", consultar)
    monkeypatch.setattr(servico, "obter_unidade_id", AsyncMock(return_value=8))
    monkeypatch.setattr(servico, "gerar_vetor_operacional", AsyncMock(return_value=[0.1]))
    ponto = SimpleNamespace(payload={cfg.QDRANT_CAMPO_UNIDADE: 8, cfg.QDRANT_CAMPO_ATIVO: True,
                                    cfg.QDRANT_CAMPO_ENTIDADE_ID: 12, cfg.QDRANT_CAMPO_TEXTO: "Torneira"})
    cliente = SimpleNamespace(query_points=AsyncMock(return_value=SimpleNamespace(points=[ponto])))

    @asynccontextmanager
    async def abrir():
        yield cliente

    monkeypatch.setattr(servico, "abrir_cliente_qdrant", abrir)
    usuario = UsuarioContexto.model_construct(usuario_id=7, tipo_acesso="gestor")
    assert asyncio.run(servico.buscar_proprias_pendentes(usuario, "torneira"))[0]["id"] == 12
    _, sql, parametros = consultar.await_args.args
    assert "p.usuario_id = :usuario_id" in sql and "p.status = 0" in sql
    assert parametros == {"usuario_id": 7, "unidade_id": 8}
    filtro = cliente.query_points.await_args.kwargs["query_filter"].model_dump()
    assert {"key": cfg.QDRANT_CAMPO_ENTIDADE_ID, "match": {"any": [12]}, "range": None,
            "geo_bounding_box": None, "geo_radius": None, "geo_polygon": None,
            "values_count": None, "is_empty": None, "is_null": None} in filtro["must"]


@pytest.mark.parametrize("acao", ["manter", "adicionar", "substituir"])
def test_campos_e_fotos_usam_mesma_transacao_sem_cloudinary(monkeypatch, acao):
    registro_atual = registro()
    monkeypatch.setattr(servico, "_ler", AsyncMock(return_value=registro_atual))
    monkeypatch.setattr(servico, "obter_unidade_id", AsyncMock(return_value=8))
    conexao = SimpleNamespace(execute=AsyncMock())
    transacao = []

    @asynccontextmanager
    async def begin():
        transacao.append("iniciada")
        yield conexao
        transacao.append("commit")

    monkeypatch.setattr(servico, "obter_motor", lambda _: SimpleNamespace(begin=begin))
    imagens = [] if acao == "manter" else ["https://example.com/nova.jpg"]
    resultado = asyncio.run(servico.atualizar_propria_pendente(
        UsuarioContexto.model_construct(usuario_id=7, tipo_acesso="gestor"),
        {"registro_id": 12, "original": servico.snapshot(registro_atual),
         "alteracoes": {"titulo": "Novo", "descricao_local": "Entrada"}, "imagens": imagens, "acao_fotos": acao},
    ))
    assert resultado == {"id": 12, "titulo": "Novo"}
    assert transacao == ["iniciada", "commit"]
    assert servico._ler.await_args.kwargs == {"travar": True}
    comandos = [str(chamada.args[0]) for chamada in conexao.execute.await_args_list]
    assert "titulo = :novo_titulo" in comandos[0] and "descricao_local = :novo_descricao_local" in comandos[0]
    assert "usuario_id = :usuario_id AND status = 0" in comandos[0]
    assert any("DELETE FROM foto" in comando for comando in comandos) == (acao == "substituir")
    assert any("INSERT INTO foto" in comando for comando in comandos) == (acao != "manter")


@pytest.mark.parametrize("motivo", ["status", "conteudo"])
def test_status_ou_conteudo_alterado_bloqueia_todas_as_gravacoes(monkeypatch, motivo):
    atual = None if motivo == "status" else {**registro(), "titulo": "Mudou no aplicativo"}
    monkeypatch.setattr(servico, "_ler", AsyncMock(return_value=atual))
    monkeypatch.setattr(servico, "obter_unidade_id", AsyncMock(return_value=8))
    conexao = SimpleNamespace(execute=AsyncMock())

    @asynccontextmanager
    async def begin():
        yield conexao

    monkeypatch.setattr(servico, "obter_motor", lambda _: SimpleNamespace(begin=begin))
    assert asyncio.run(servico.atualizar_propria_pendente(
        UsuarioContexto.model_construct(usuario_id=7, tipo_acesso="tecnico"),
        {"registro_id": 12, "original": servico.snapshot(registro()), "alteracoes": {"titulo": "Novo"},
         "imagens": ["https://example.com/nova.jpg"], "acao_fotos": "substituir"},
    )) is None
    conexao.execute.assert_not_awaited()


def test_falha_ao_inserir_foto_aborta_a_transacao(monkeypatch):
    monkeypatch.setattr(servico, "_ler", AsyncMock(return_value=registro()))
    monkeypatch.setattr(servico, "obter_unidade_id", AsyncMock(return_value=8))
    comandos, encerramento = [], []

    async def executar(sql, parametros):
        comandos.append(str(sql))
        if "INSERT INTO foto" in str(sql):
            raise RuntimeError("Falha de inserção")

    @asynccontextmanager
    async def begin():
        try:
            yield SimpleNamespace(execute=executar)
        except Exception:
            encerramento.append("rollback")
            raise
        else:
            encerramento.append("commit")

    monkeypatch.setattr(servico, "obter_motor", lambda _: SimpleNamespace(begin=begin))
    with pytest.raises(RuntimeError, match="Falha de inserção"):
        asyncio.run(servico.atualizar_propria_pendente(
            UsuarioContexto.model_construct(usuario_id=7, tipo_acesso="tecnico"),
            {"registro_id": 12, "original": servico.snapshot(registro()), "alteracoes": {"titulo": "Novo"},
             "imagens": ["https://example.com/nova.jpg"], "acao_fotos": "substituir"},
        ))
    assert encerramento == ["rollback"]
    assert any("UPDATE problema" in sql for sql in comandos)
    assert any("DELETE FROM foto" in sql for sql in comandos)


@pytest.mark.parametrize("etapa", ["selecao", "final"])
@pytest.mark.parametrize("falhar", [False, True])
def test_confirmacao_so_fica_disponivel_depois_de_persistir_resposta(monkeypatch, fluxo, etapa, falhar):
    from app.graph import executor
    selecao = asyncio.run(selecionar(fluxo, titulo="Novo título"))
    if etapa == "final":
        apresentar(fluxo, selecao)
        turno(fluxo, "Sim")
        asyncio.run(ferramentas.atualizar_solicitacao.coroutine(fluxo.runtime))
    proposta = metadados_proposta(fluxo.atual)
    retorno = {"resposta_final": proposta["resumo_confirmacao"], "propostas_apresentadas": [proposta], "intencao": "solicitacao"}
    monkeypatch.setattr(executor, "grafo", SimpleNamespace(get_state=lambda _: SimpleNamespace(values={}),
                                                         ainvoke=AsyncMock(return_value=retorno)))
    for nome, valor in {"obter_documento_sessao_id": "documento", "recuperar_mensagens": [],
                        "obter_rascunho_solicitacao": fluxo.atual, "obter_acao": None,
                        "obter_analise_compra": None, "obter_quantidade_anexos_pendentes": 0}.items():
        monkeypatch.setattr(executor, nome, AsyncMock(return_value=valor))
    papeis = []

    async def salvar(sessao, papel, *args, **kwargs):
        papeis.append(papel)
        if falhar and papel == "assistant":
            raise ConnectionError("Falha simulada")

    monkeypatch.setattr(executor, "salvar_mensagem", salvar)
    marcador = AsyncMock(return_value=True)
    monkeypatch.setattr(executor, "atualizar_rascunho_solicitacao", marcador)
    monkeypatch.setattr(executor, "marcar_confirmacao_mensagem", AsyncMock())
    if falhar:
        with pytest.raises(ConnectionError):
            asyncio.run(executor.executar_grafo("Quero atualizar", fluxo.contexto["usuario"], "sessao"))
        marcador.assert_not_awaited()
    else:
        asyncio.run(executor.executar_grafo("Quero atualizar", fluxo.contexto["usuario"], "sessao"))
        assert papeis == ["human", "assistant"]
        campos = marcador.await_args.args[2]
        assert ("versao_selecao_apresentada" in campos) == (etapa == "selecao")
        assert ("atualizacao_apresentada" in campos) == (etapa == "final")
