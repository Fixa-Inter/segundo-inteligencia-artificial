"""Edição de ocorrências: autoria, atividade, duas confirmações e escrita atômica."""

import asyncio
import json
from contextlib import asynccontextmanager
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.agents import ajuda_geral, solicitacoes
from app.core import configuracao as cfg
from app.core.propostas import metadados_proposta
from app.graph import continuacoes, operacoes, propostas
from app.schemas import UsuarioContexto
from app.services.ocorrencias import atualizarOcorrencia as servico
from app.services.operacoes import aprovacao_operacoes, dados_atualizacao
from app.tools.ocorrencias import atualizarOcorrencia as ferramentas
from app.tests.test_operacoes_aprovadas import documentos


def registro():
    return {"id": 12, "titulo": "Troca da torneira", "descricao_ocorrencia": "Torneira substituída",
            "descricao_local": "Entrada", "local_unidade_id": 2, "categoria_equipamento_id": 3,
            "categoria_problema": 2, "prioridade": 1, "local": "Sala 2", "categoria_equipamento": "Torneiras",
            "fotos": [{"id": 9, "url": "https://example.com/antiga.jpg"}]}


@pytest.fixture
def fluxo(monkeypatch):
    atual = {"id": "rascunho", "tipo": "ocorrencia", "operacao": "atualizar", "versao": 1,
             "status_fluxo": "coletando_dados", "dados": {}, "imagens": [], "pausado": False,
             "turno_id": "busca", "dados_confirmados": {}}
    contexto = {"usuario": UsuarioContexto.model_construct(usuario_id=7, tipo_acesso="tecnico", access_token="teste"),
                "session_id": "sessao", "turno_id": "busca", "mensagem_atual": "Quero alterar a ocorrência",
                "imagens": [], "operacoes_pendentes": [], "resultados_operacoes": []}
    tipos_salvos = []

    async def obter(*args, **kwargs):
        assert kwargs["tipo"] == "ocorrencia"
        return deepcopy(atual)

    async def salvar(sessao, usuario_id, campos, **controle):
        assert sessao == "sessao" and usuario_id == 7 and controle["tipo"] == "ocorrencia"
        tipos_salvos.append(controle["tipo"])
        if (controle.get("rascunho_id") != atual["id"] or controle.get("versao") != atual["versao"]
                or atual["status_fluxo"] not in controle.get("status_esperados", [])):
            return False
        atual.update(deepcopy(campos))
        return True

    monkeypatch.setattr(ferramentas, "obter_rascunho_solicitacao", obter)
    monkeypatch.setattr(ferramentas, "atualizar_rascunho_solicitacao", salvar)
    monkeypatch.setattr(ferramentas, "registrar_coleta_parcial", obter)
    monkeypatch.setattr(servico, "buscar_proprias_ativas", AsyncMock(return_value=[registro()]))
    monkeypatch.setattr(servico, "consultar_propria_ativa", AsyncMock(return_value=registro()))
    monkeypatch.setattr(servico, "localizar_opcao", AsyncMock(return_value={"id": 4, "nome": "Sala 4"}))
    gravar = AsyncMock(return_value={"id": 12})
    monkeypatch.setattr(servico, "atualizar_propria_ativa", gravar)
    return SimpleNamespace(atual=atual, contexto=contexto, runtime=SimpleNamespace(context=contexto),
                           gravar=gravar, tipos_salvos=tipos_salvos)


def turno(fluxo, mensagem, imagens=None):
    fluxo.contexto["turno_id"] += "-seguinte"
    fluxo.contexto["mensagem_atual"] = mensagem
    fluxo.contexto["imagens"] = imagens or []


async def selecionar(fluxo, **alteracoes):
    await ferramentas.buscar_ocorrencias_para_atualizar.coroutine("torneira", fluxo.runtime)
    return await ferramentas.atualizar_ocorrencia.coroutine(fluxo.runtime, ocorrencia_id=12, **alteracoes)


def apresentar(fluxo, resposta):
    proposta = resposta["proposta"]
    if proposta["etapa"] == "selecao":
        fluxo.atual.update(turno_selecao_apresentada=fluxo.contexto["turno_id"],
                           versao_selecao_apresentada=proposta["versao"])
    else:
        fluxo.atual.update(turno_apresentacao=fluxo.contexto["turno_id"],
                           atualizacao_apresentada=deepcopy(proposta["atualizacao"]))


@pytest.mark.parametrize("perfil", ["solicitante", "tecnico", "gestor", "administrador"])
def test_ferramentas_expostas_apenas_aos_tres_perfis_autorizados(monkeypatch, perfil):
    monkeypatch.setattr(ajuda_geral, "create_agent", lambda **kwargs: kwargs)
    monkeypatch.setattr(solicitacoes, "create_agent", lambda **kwargs: kwargs)
    consulta = ajuda_geral.criar_agente_ajuda_geral(object(), "teste", perfil=perfil)
    cadastro = solicitacoes.criar_agente_solicitacoes(object(), "teste", **{
        "gestor" if perfil == "administrador" else perfil: True,
    })
    for agente in (consulta, cadastro):
        for tool in (ferramentas.buscar_ocorrencias_para_atualizar, ferramentas.atualizar_ocorrencia):
            assert (tool in agente["tools"]) == (perfil != "solicitante")


def test_solicitante_nao_consegue_chamar_tools_diretamente(fluxo):
    fluxo.contexto["usuario"].tipo_acesso = "solicitante"
    for chamada in (ferramentas.buscar_ocorrencias_para_atualizar.coroutine("torneira", fluxo.runtime),
                    ferramentas.atualizar_ocorrencia.coroutine(fluxo.runtime, ocorrencia_id=12)):
        assert asyncio.run(chamada)["status"] == "ACESSO_NEGADO"
    servico.buscar_proprias_ativas.assert_not_awaited()
    servico.consultar_propria_ativa.assert_not_awaited()


def test_selecao_mostra_apenas_titulo_descricao_e_metadados_de_ocorrencia(fluxo):
    resposta = asyncio.run(selecionar(fluxo, titulo="Novo título"))
    proposta = resposta["proposta"]
    assert proposta["tipo"] == "ocorrencia"
    assert proposta["resumo_confirmacao"] == "A ocorrência que você quer alterar é esta?\n\n**Troca da torneira**  \nTorneira substituída"
    evidencia = json.dumps({"ferramenta": "atualizar_ocorrencia", "status_execucao": "success", "resultado": resposta})
    assert propostas.propostas_resposta({"evidencias": [evidencia]}) == [proposta]
    assert set(fluxo.tipos_salvos) == {"ocorrencia"}


@pytest.mark.parametrize("apresentada,novo_turno", [(False, True), (True, False)])
def test_selecao_exige_apresentacao_persistida_em_outro_turno(fluxo, apresentada, novo_turno):
    selecao = asyncio.run(selecionar(fluxo, titulo="Novo título"))
    if apresentada:
        apresentar(fluxo, selecao)
    if novo_turno:
        turno(fluxo, "Sim")
    else:
        fluxo.contexto["mensagem_atual"] = "Sim"
    assert asyncio.run(ferramentas.atualizar_ocorrencia.coroutine(fluxo.runtime))["proposta"]["etapa"] == "selecao"
    assert fluxo.contexto["operacoes_pendentes"] == []


def test_primeiro_aceite_preserva_campos_e_mostra_enums_legiveis(fluxo):
    selecao = asyncio.run(selecionar(fluxo, titulo="Revisão da torneira", categoria_problema="MECANICA", prioridade="ALTA"))
    apresentar(fluxo, selecao)
    turno(fluxo, "É essa")
    final = asyncio.run(ferramentas.atualizar_ocorrencia.coroutine(fluxo.runtime))
    texto = final["proposta"]["resumo_confirmacao"]
    assert "Mecânica" in texto and "ALTA" in texto and "Sala 2" in texto
    assert "Torneira substituída" in texto and "manter as 1 fotos" in texto
    assert final["proposta"]["dados"]["categoria_problema"] == 3
    assert final["proposta"]["dados"]["prioridade"] == 0
    assert fluxo.contexto["operacoes_pendentes"] == []
    fluxo.gravar.assert_not_awaited()


@pytest.mark.parametrize("incerto", [False, True])
def test_so_executor_aprovado_grava_uma_vez(fluxo, documentos, incerto):
    if incerto:
        fluxo.gravar.side_effect = TimeoutError("Resultado desconhecido")

    async def verificar():
        selecao = await selecionar(fluxo, titulo="Título atualizado", prioridade="BAIXA")
        apresentar(fluxo, selecao)
        turno(fluxo, "Sim")
        final = await ferramentas.atualizar_ocorrencia.coroutine(fluxo.runtime)
        apresentar(fluxo, final)
        turno(fluxo, "Pode atualizar")
        assert (await ferramentas.atualizar_ocorrencia.coroutine(fluxo.runtime))["status"] == "OPERACAO_PREPARADA"
        fluxo.gravar.assert_not_awaited()
        estado = {"operacoes_pendentes": deepcopy(fluxo.contexto["operacoes_pendentes"]), "veredito": "bloqueado"}
        await operacoes.executar_operacoes(estado, fluxo.runtime)
        fluxo.gravar.assert_not_awaited()
        estado.update(veredito="aprovado", aprovacao_operacoes=aprovacao_operacoes(estado["operacoes_pendentes"], fluxo.contexto))
        resultado = await operacoes.executar_operacoes(estado, fluxo.runtime)
        assert resultado["resultados_operacoes"][0]["resultado"]["status"] == ("RESULTADO_INDETERMINADO" if incerto else "SUCESSO")
        if not incerto:
            assert resultado["resposta_final"] == "Ocorrência atualizada com sucesso."
        await operacoes.executar_operacoes(estado, fluxo.runtime)
        turno(fluxo, "Sim")
        assert (await ferramentas.atualizar_ocorrencia.coroutine(fluxo.runtime))["status"] == ("RESULTADO_INDETERMINADO" if incerto else "JA_CONCLUIDA")
        fluxo.gravar.assert_awaited_once()
    asyncio.run(verificar())


@pytest.mark.parametrize("campo", ["prioridade", "categoria_problema", "imagens", "registro_id"])
def test_mudanca_depois_da_apresentacao_exige_nova_conferencia(fluxo, campo):
    async def verificar():
        selecao = await selecionar(fluxo, titulo="Novo título")
        apresentar(fluxo, selecao)
        turno(fluxo, "Sim")
        final = await ferramentas.atualizar_ocorrencia.coroutine(fluxo.runtime)
        apresentar(fluxo, final)
        aprovado = deepcopy(dados_atualizacao(fluxo.atual))
        turno(fluxo, "Pode atualizar")
        if campo in {"prioridade", "categoria_problema"}:
            fluxo.atual["alteracoes"][campo] = 2
        elif campo == "imagens":
            fluxo.atual["imagens"] = ["https://example.com/outra.jpg"]
        else:
            fluxo.atual["registro_id"] = 99
        assert (await ferramentas.processar_atualizacao(fluxo.runtime, operacao_aprovada=aprovado))["status"] == "AGUARDANDO_CONFIRMACAO"
        fluxo.gravar.assert_not_awaited()
    asyncio.run(verificar())


@pytest.mark.parametrize("acao", ["adicionar", "substituir"])
def test_fotos_iniciais_sao_preservadas_e_exigem_escolha_explicita(fluxo, acao):
    fluxo.contexto["imagens"] = ["https://example.com/nova.jpg"]
    selecao = asyncio.run(selecionar(fluxo, titulo="Novo título"))
    apresentar(fluxo, selecao)
    turno(fluxo, "Sim")
    assert asyncio.run(ferramentas.atualizar_ocorrencia.coroutine(fluxo.runtime, acao_fotos=acao))["status"] == "AGUARDANDO_INFORMACAO"
    turno(fluxo, f"Quero {acao} as fotos")
    final = asyncio.run(ferramentas.atualizar_ocorrencia.coroutine(fluxo.runtime, acao_fotos=acao))
    assert final["proposta"]["atualizacao"]["acao_fotos"] == acao
    assert final["proposta"]["atualizacao"]["imagens"] == ["https://example.com/nova.jpg"]


@pytest.mark.parametrize("nome,identificador", [
    ("ELETRICA", 1), ("HIDRAULICA", 2), ("MECANICA", 3), ("INFORMATICA", 4),
    ("MOBILIARIO", 5), ("CLIMATIZACAO", 6), ("REDE_CONECTIVIDADE", 7),
    ("SEGURANCA", 8), ("ILUMINACAO", 9), ("LIMPEZA_CONSERVACAO", 10),
])
def test_categorias_seguem_ids_do_contrato(nome, identificador):
    assert servico.validar_alteracoes({"categoria_problema": nome}) == {"categoria_problema": identificador}
    assert 1 <= identificador <= 10


@pytest.mark.parametrize("valor", [True, False, -1, 3, 1.5, "URGENTE"])
def test_prioridade_invalida_nao_e_aceita(valor):
    with pytest.raises(ValueError):
        servico.validar_alteracoes({"prioridade": valor})


def test_nao_seleciona_id_fora_dos_candidatos(fluxo):
    asyncio.run(ferramentas.buscar_ocorrencias_para_atualizar.coroutine("torneira", fluxo.runtime))
    assert asyncio.run(ferramentas.atualizar_ocorrencia.coroutine(fluxo.runtime, ocorrencia_id=99))["status"] == "ERRO_VALIDACAO"
    servico.consultar_propria_ativa.assert_not_awaited()


@pytest.mark.parametrize("perfil", ["tecnico", "gestor", "administrador"])
def test_busca_qdrant_restringe_autor_unidade_e_atividade(monkeypatch, perfil):
    consulta = AsyncMock(return_value=[registro()])
    monkeypatch.setattr(servico, "executar_consulta", consulta)
    monkeypatch.setattr(servico, "obter_unidade_id", AsyncMock(return_value=8))
    monkeypatch.setattr(servico, "gerar_vetor_operacional", AsyncMock(return_value=[0.1]))
    ponto = SimpleNamespace(payload={cfg.QDRANT_CAMPO_UNIDADE: 8, cfg.QDRANT_CAMPO_ATIVO: True,
                                    cfg.QDRANT_CAMPO_ENTIDADE_ID: 12, cfg.QDRANT_CAMPO_TEXTO: "Troca da torneira"})
    cliente = SimpleNamespace(query_points=AsyncMock(return_value=SimpleNamespace(points=[ponto])))

    @asynccontextmanager
    async def abrir():
        yield cliente

    monkeypatch.setattr(servico, "abrir_cliente_qdrant", abrir)
    usuario = UsuarioContexto.model_construct(usuario_id=7, tipo_acesso=perfil)
    assert asyncio.run(servico.buscar_proprias_ativas(usuario, "torneira"))[0]["id"] == 12
    _, sql, parametros = consulta.await_args.args
    assert "o.usuario_id = :usuario_id" in sql and "o.esta_ativo IS TRUE" in sql and "status" not in sql
    assert parametros == {"usuario_id": 7, "unidade_id": 8}
    chamada = cliente.query_points.await_args.kwargs
    assert chamada["collection_name"] == "ocorrencia"
    assert any(getattr(condicao.match, "any", None) == [12] for condicao in chamada["query_filter"].must)


@pytest.mark.parametrize("perfil", ["tecnico", "gestor", "administrador"])
def test_leitura_com_trava_exige_autoria_e_atividade_para_todos(monkeypatch, perfil):
    usuario = UsuarioContexto.model_construct(usuario_id=7, tipo_acesso=perfil)
    resultado = SimpleNamespace(mappings=lambda: SimpleNamespace(first=registro))
    fotos = SimpleNamespace(mappings=lambda: SimpleNamespace(all=lambda: registro()["fotos"]))
    conexao = SimpleNamespace(execute=AsyncMock(side_effect=[resultado, fotos]))
    asyncio.run(servico._ler(conexao, usuario, {"registro_id": 12, "usuario_id": 7, "unidade_id": 8}, travar=True))
    sql = str(conexao.execute.await_args_list[0].args[0])
    assert "o.usuario_id = :usuario_id" in sql and "o.esta_ativo IS TRUE" in sql
    assert "local.unidade_id = :unidade_id" in sql and "FOR UPDATE OF o" in sql and "status" not in sql
    assert "ocorrencia_id = :registro_id" in str(conexao.execute.await_args_list[1].args[0])


@pytest.mark.parametrize("acao", ["manter", "adicionar", "substituir"])
def test_transacao_altera_campos_enums_e_fotos_da_ocorrencia(monkeypatch, acao):
    monkeypatch.setattr(servico, "_ler", AsyncMock(return_value=registro()))
    monkeypatch.setattr(servico, "obter_unidade_id", AsyncMock(return_value=8))
    conexao = SimpleNamespace(execute=AsyncMock(return_value=SimpleNamespace(first=lambda: {"id": 12})))
    transacao = []

    @asynccontextmanager
    async def begin():
        transacao.append("iniciada")
        yield conexao
        transacao.append("commit")

    monkeypatch.setattr(servico, "obter_motor", lambda _: SimpleNamespace(begin=begin))
    resultado = asyncio.run(servico.atualizar_propria_ativa(
        UsuarioContexto.model_construct(usuario_id=7, tipo_acesso="gestor"),
        {"registro_id": 12, "original": servico.snapshot(registro()),
         "alteracoes": {"titulo": "Novo", "categoria_problema": "MECANICA", "prioridade": "ALTA"},
         "imagens": [] if acao == "manter" else ["https://example.com/nova.jpg"], "acao_fotos": acao},
    ))
    assert resultado == {"id": 12, "titulo": "Novo"} and transacao == ["iniciada", "commit"]
    assert servico._ler.await_args.kwargs == {"travar": True}
    comandos = [str(chamada.args[0]) for chamada in conexao.execute.await_args_list]
    assert "UPDATE ocorrencia" in comandos[0] and "usuario_id = :usuario_id AND esta_ativo IS TRUE" in comandos[0]
    parametros = conexao.execute.await_args_list[0].args[1]
    assert parametros["novo_prioridade"] == 0 and parametros["novo_categoria_problema"] == 3
    assert any("DELETE FROM foto WHERE ocorrencia_id" in sql for sql in comandos) == (acao == "substituir")
    assert any("INSERT INTO foto (ocorrencia_id, url)" in sql for sql in comandos) == (acao != "manter")
    assert not any("problema_id" in sql for sql in comandos)


@pytest.mark.parametrize("motivo", ["inativa_ou_outro_autor", "dados_alterados"])
def test_registro_indisponivel_ou_modificado_nao_sofre_escritas(monkeypatch, motivo):
    atual = None if motivo == "inativa_ou_outro_autor" else {**registro(), "prioridade": 0}
    monkeypatch.setattr(servico, "_ler", AsyncMock(return_value=atual))
    monkeypatch.setattr(servico, "obter_unidade_id", AsyncMock(return_value=8))
    conexao = SimpleNamespace(execute=AsyncMock())

    @asynccontextmanager
    async def begin():
        yield conexao

    monkeypatch.setattr(servico, "obter_motor", lambda _: SimpleNamespace(begin=begin))
    assert asyncio.run(servico.atualizar_propria_ativa(
        UsuarioContexto.model_construct(usuario_id=7, tipo_acesso="administrador"),
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
        return SimpleNamespace(first=lambda: {"id": 12})

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
        asyncio.run(servico.atualizar_propria_ativa(
            UsuarioContexto.model_construct(usuario_id=7, tipo_acesso="tecnico"),
            {"registro_id": 12, "original": servico.snapshot(registro()), "alteracoes": {"prioridade": "ALTA"},
             "imagens": ["https://example.com/nova.jpg"], "acao_fotos": "substituir"},
        ))
    assert encerramento == ["rollback"]
    assert any("UPDATE ocorrencia" in sql for sql in comandos)
    assert any("DELETE FROM foto WHERE ocorrencia_id" in sql for sql in comandos)


def test_foto_recebida_invalida_proposta_sem_modificar_solicitacao(monkeypatch, fluxo):
    from app.memory.persistencia import rascunho_solicitacao as persistencia
    fluxo.atual.update(status_fluxo="aguardando_confirmacao", etapa="final", selecao_confirmada=True,
                        acao_fotos="manter")
    outra = {**deepcopy(fluxo.atual), "tipo": "solicitacao", "id": "outra", "versao": 10}
    colecao = SimpleNamespace(find_one=AsyncMock(return_value={"ocorrencia_pendente": deepcopy(fluxo.atual),
                                                              "solicitacao_pendente": outra}),
                             update_one=AsyncMock(return_value=SimpleNamespace(matched_count=1)))

    @asynccontextmanager
    async def abrir():
        yield {persistencia.MONGO_BANCO_DADOS: {persistencia.MONGO_COLECAO_SESSOES: colecao}}

    monkeypatch.setattr(persistencia, "abrir_cliente_mongo", abrir)
    monkeypatch.setattr(persistencia, "obter_documento_sessao_id", AsyncMock(return_value="documento"))
    asyncio.run(persistencia.adicionar_imagens_sessao("sessao", 7, ["https://example.com/nova.jpg"], tipo="ocorrencia"))
    filtro, alteracao = colecao.update_one.await_args.args
    assert filtro["ocorrencia_pendente.id"] == fluxo.atual["id"]
    campos = alteracao["$set"]
    assert campos["ocorrencia_pendente.versao"] == fluxo.atual["versao"] + 1
    assert campos["ocorrencia_pendente.status_fluxo"] == "coletando_dados"
    assert campos["ocorrencia_pendente.acao_fotos"] is None
    assert not any(chave.startswith("solicitacao_pendente.") for chave in campos)


def test_roteador_e_supervisor_encaminham_atualizacao_de_ocorrencia(monkeypatch, fluxo):
    from app.agents import orquestrador
    from app.graph import nos
    from langchain_core.messages import HumanMessage
    decisao = orquestrador.DecisaoRoteamento(
        intencao="ocorrencia", operacao_ocorrencia="atualizar", continua_pendente=False,
        cadastro_em_andamento=False, justificativa="Atualização explícita",
    )
    monkeypatch.setattr(orquestrador, "roteador_estruturado", SimpleNamespace(ainvoke=AsyncMock(return_value=decisao)))
    estado = {"messages": [HumanMessage(content="Altere a descrição da minha ocorrência da torneira")]}
    retorno = asyncio.run(orquestrador.rotear_orquestrador(estado, estado["messages"][-1].content))
    assert retorno.intencao == "ocorrencia" and retorno.operacao_ocorrencia == "atualizar"
    monkeypatch.setattr(nos, "rotear_orquestrador", AsyncMock(return_value=retorno))
    resultado = asyncio.run(nos.supervisionar(estado, fluxo.runtime))
    assert resultado["intencao"] == "ocorrencia" and resultado["operacao_ocorrencia"] == "atualizar"


@pytest.mark.parametrize("cadastro", [True, False])
def test_no_guarda_coleta_como_atualizacao_e_injeta_a_ferramenta_correta(monkeypatch, fluxo, cadastro):
    from app.graph import nos
    from app.agents.agentsResult import SolicitacaoOcorrenciaResultado
    from langchain_core.messages import HumanMessage, SystemMessage
    coletar = AsyncMock(return_value=fluxo.atual)
    monkeypatch.setattr(nos, "registrar_coleta_parcial", coletar)
    monkeypatch.setattr(nos, "obter_rascunho_solicitacao", AsyncMock(return_value=fluxo.atual))

    async def executar(agente, estado, contexto, formato):
        textos = [mensagem.content for mensagem in estado["messages"] if isinstance(mensagem, SystemMessage)]
        assert any("atualizar_ocorrencia" in texto for texto in textos)
        assert contexto["intencao_atual"] == "ocorrencia"
        return {"structured_response": SolicitacaoOcorrenciaResultado(
            agente="solicitacoes", resposta="Qual ocorrência você quer alterar?", status="AGUARDANDO_INFORMACAO",
        )}, []

    monkeypatch.setattr(nos, "executar_com_evidencias", executar)
    resultado = asyncio.run(nos.executar_solicitacao(
        {"perfil": "tecnico", "intencao": "ocorrencia", "operacao_ocorrencia": "atualizar",
         "cadastro_em_andamento": cadastro, "messages": [HumanMessage(content="Quero alterar uma ocorrência")],
         "evidencias": [], "ocorrencia_pendente": fluxo.atual}, fluxo.runtime,
    ))
    assert resultado["erro"] is None
    assert coletar.await_args.kwargs["tipo"] == "ocorrencia"
    assert coletar.await_args.kwargs["operacao"] == "atualizar"


def test_continuacao_preserva_modo_ocorrencia_sem_usar_rascunho_de_solicitacao(fluxo):
    asyncio.run(selecionar(fluxo, titulo="Novo título"))
    estado = {"ocorrencia_pendente": fluxo.atual,
              "solicitacao_pendente": {"tipo": "solicitacao", "operacao": "criar", "pausado": True,
                                        "status_fluxo": "coletando_dados"}}
    resposta = asyncio.run(continuacoes.tratar_continuacao(estado, fluxo.contexto, "Sim"))
    assert resposta["intencao"] == "ocorrencia" and resposta["operacao_ocorrencia"] == "atualizar"
    assert resposta["operacao_solicitacao"] == "criar"


def test_criacao_nao_processa_rascunho_de_atualizacao(monkeypatch, fluxo):
    from app.tools.ocorrencias import criarOcorrencia
    monkeypatch.setattr(criarOcorrencia, "obter_rascunho_solicitacao", AsyncMock(return_value=fluxo.atual))
    resultado = asyncio.run(criarOcorrencia.processar_ocorrencia(fluxo.runtime))
    assert resultado["status"] == "ERRO_VALIDACAO" and "atualizar ocorrência" in resultado["mensagem"]


@pytest.mark.parametrize("etapa", ["selecao", "final"])
@pytest.mark.parametrize("falhar", [False, True])
def test_confirmacao_so_e_marcada_depois_de_persistir_a_resposta(monkeypatch, fluxo, etapa, falhar):
    from app.graph import executor
    selecao = asyncio.run(selecionar(fluxo, titulo="Novo título"))
    if etapa == "final":
        apresentar(fluxo, selecao)
        turno(fluxo, "Sim")
        asyncio.run(ferramentas.atualizar_ocorrencia.coroutine(fluxo.runtime))
    proposta = metadados_proposta(fluxo.atual)
    retorno = {"resposta_final": proposta["resumo_confirmacao"], "propostas_apresentadas": [proposta], "intencao": "ocorrencia"}
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
        assert papeis == ["human", "assistant"] and marcador.await_args.kwargs["tipo"] == "ocorrencia"
        campos = marcador.await_args.args[2]
        assert ("versao_selecao_apresentada" in campos) == (etapa == "selecao")
        assert ("atualizacao_apresentada" in campos) == (etapa == "final")
