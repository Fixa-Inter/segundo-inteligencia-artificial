"""O administrador conserva a identidade e as restrições de um técnico."""

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


def test_agentes_e_conexao_do_administrador_seguem_tecnico():
    assert set(AGENTES_POR_PERFIL["ajuda_geral"]) >= {"tecnico", "administrador"}
    assert set(AGENTES_POR_PERFIL["faq"]) >= {"tecnico", "administrador"}
    assert set(AGENTES_POR_PERFIL["solicitacao"]) >= {"tecnico", "administrador"}
    assert "administrador" not in AGENTES_POR_PERFIL["analytics"]
    assert "administrador" not in AGENTES_POR_PERFIL["visualizacao"]
    assert postgres._URLS_POR_PERFIL["administrador"] == postgres._URLS_POR_PERFIL["tecnico"]


def test_consultas_do_administrador_exigem_propriedade_e_unidade(monkeypatch):
    usuario = usuario_administrador()
    consulta = AsyncMock(return_value=[])
    monkeypatch.setattr(ordens, "executar_consulta", consulta)

    asyncio.run(ordens.buscar_ordens_servico(usuario, status="Atrasada"))
    perfil, sql, parametros = consulta.await_args.args
    assert perfil == "administrador"
    assert "os.usuario_id = :usuario_id" in sql
    assert "unidade_registro.cnpj = unidade_autenticada.cnpj" in sql
    assert parametros["usuario_id"] == usuario.usuario_id
    assert "o.usuario_id = :usuario_id" in _sql_alvo("ocorrencia", usuario)
    assert "os.usuario_id = :usuario_id" in _sql_alvo("observacao_conclusao", usuario)


def test_faq_do_administrador_consulta_documentos_do_tecnico(monkeypatch):
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
    assert filtro.must[0].match.value == "tecnico"
