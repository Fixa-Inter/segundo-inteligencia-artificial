"""O administrador conserva a identidade e possui as permissões de gestor."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastapi.security import HTTPAuthorizationCredentials
from langchain_core.messages import HumanMessage

from app.api.dependencies import auth
from app.agents.registro import AGENTES_POR_PERFIL
from app.core.clients import postgres
from app.graph import nos
from app.graph.executor import criar_estado_inicial
from app.schemas import ConversaSaida, UsuarioContexto
from app.services.ajuda_geral.edicoes import _sql_alvo
from app.services.ordensServico import buscarOrdensServico as ordens
from app.tools.faq import buscar as faq


def usuario_administrador() -> UsuarioContexto:
    return UsuarioContexto(
        access_token="token", usuario_id=17, nome_completo="Administrador",
        email="admin@exemplo.com", tipo_acesso="ADMINISTRADOR",
        cnpj_endereco="12.345.678/0001-90",
    )


def test_perfil_autenticado_percorre_grafo_e_resposta(monkeypatch):
    monkeypatch.setattr(auth, "consultar_perfil", AsyncMock(return_value={
        "id": 17, "nomeCompleto": "Administrador", "email": "admin@exemplo.com",
        "tipoAcesso": "ADMINISTRADOR", "cnpjUnidade": "12.345.678/0001-90",
    }))
    usuario = asyncio.run(auth.obter_usuario_atual(
        HTTPAuthorizationCredentials(scheme="Bearer", credentials="token"),
    ))
    assert usuario.tipo_acesso == "administrador"
    assert usuario.cnpj_endereco == "12345678000190"

    estado = criar_estado_inicial([HumanMessage(content="Olá")], usuario)
    assert estado["perfil"] == "administrador"
    monkeypatch.setattr(nos, "proteger_entrada", lambda _: {"bloqueado": False})
    assert nos.validar_entrada({**estado, "mensagem_anonimizada": "Olá"})["entrada_valida"]
    assert ConversaSaida(
        thread_id="sessao", intencao="analista_compras", resposta="Busca concluída",
    ).intencao == "analista_compras"


def test_agentes_e_conexao_do_administrador_seguem_gestor():
    assert set(AGENTES_POR_PERFIL["ajuda_geral"]) >= {"gestor", "administrador"}
    assert set(AGENTES_POR_PERFIL["faq"]) >= {"gestor", "administrador"}
    assert set(AGENTES_POR_PERFIL["solicitacao"]) >= {"gestor", "administrador"}
    assert "administrador" in AGENTES_POR_PERFIL["analytics"]
    assert "administrador" in AGENTES_POR_PERFIL["visualizacao"]
    assert postgres._URLS_POR_PERFIL["administrador"] == postgres._URLS_POR_PERFIL["gestor"]


def test_ferramentas_registradas_do_administrador_sao_identicas_as_do_gestor():
    for agentes in AGENTES_POR_PERFIL.values():
        if "gestor" not in agentes:
            continue
        gestor = agentes["gestor"].get_graph().nodes["tools"].data
        administrador = agentes["administrador"].get_graph().nodes["tools"].data
        assert set(administrador.tools_by_name) == set(gestor.tools_by_name)


def test_prompt_administrador_herda_gestor_preservando_identidade():
    from app.agents.prompts.reutilizaveis import ADMINISTRADOR_INSTRUCAO, GESTOR_INSTRUCAO, TECNICO_INSTRUCAO
    assert GESTOR_INSTRUCAO in ADMINISTRADOR_INSTRUCAO
    assert TECNICO_INSTRUCAO not in ADMINISTRADOR_INSTRUCAO
    assert "perfil administrador" in ADMINISTRADOR_INSTRUCAO


def test_administrador_nao_recebe_criacao_exclusiva_de_tecnico_e_solicitante():
    from app.tools.solicitacoes import criar_solicitacao, salvar_rascunho_solicitacao
    runtime = SimpleNamespace(context={"usuario": usuario_administrador(), "session_id": "sessao", "turno_id": "turno"})
    resultado = asyncio.run(criar_solicitacao.coroutine(runtime))
    assert resultado["status"] == "ACESSO_NEGADO"
    resumo = asyncio.run(salvar_rascunho_solicitacao.coroutine(
        categoria_equipamento_id=1, local_endereco_id=1, titulo="Teste",
        descricao_problema="Teste", descricao_local="Teste", runtime=runtime,
    ))
    assert resumo["status"] == "ACESSO_NEGADO"


def test_consultas_do_administrador_preservam_unidade_sem_restricao_de_tecnico(monkeypatch):
    usuario = usuario_administrador()
    consulta = AsyncMock(return_value=[])
    monkeypatch.setattr(ordens, "executar_consulta", consulta)

    asyncio.run(ordens.buscar_ordens_servico(usuario, status="Atrasada"))
    perfil, sql, parametros = consulta.await_args.args
    assert perfil == "administrador"
    assert "os.usuario_id = :usuario_id" not in sql
    assert "unidade_registro.cnpj = unidade_autenticada.cnpj" in sql
    assert parametros["usuario_id"] == usuario.usuario_id
    assert "o.usuario_id = :usuario_id" not in _sql_alvo("ocorrencia", usuario)
    assert "os.usuario_id = :usuario_id" not in _sql_alvo("observacao_conclusao", usuario)


def test_faq_do_administrador_consulta_documentos_do_gestor(monkeypatch):
    consulta = AsyncMock(return_value=SimpleNamespace(points=[]))

    class ClienteQdrant:
        async def __aenter__(self):
            return SimpleNamespace(query_points=consulta)

        async def __aexit__(self, *_):
            return None

    monkeypatch.setattr(faq, "gerar_vetor_documento", AsyncMock(return_value=[0.1]))
    monkeypatch.setattr(faq, "abrir_cliente_qdrant", ClienteQdrant)
    runtime = SimpleNamespace(context={"usuario": usuario_administrador()})

    asyncio.run(faq.buscar_faq.coroutine("Como registrar uma ocorrência?", runtime))
    filtro = consulta.await_args.kwargs["query_filter"]
    assert filtro.must[0].match.value == "gestor"
