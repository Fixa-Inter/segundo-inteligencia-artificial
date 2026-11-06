"""Roteamento, autorização e SQL real de contagens, sem serviços externos."""

import asyncio
import json
import sqlite3
from datetime import date, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from pydantic import ValidationError

from app.graph import nos, continuacoes
from app.agents import ajuda_geral, orquestrador
from app.schemas import UsuarioContexto
from app.schemas.resultados_agentes import FAQResultado
from app.services.ajuda_geral import contagens
from app.tools.ajuda_geral.contagens import contar_meus_registros, _ContagemPessoal


def usuario(perfil="solicitante"):
    return UsuarioContexto(
        access_token="teste", usuario_id=1, nome_completo="Teste",
        email="teste@exemplo.com", tipo_acesso=perfil, cnpj_endereco="12345678000190",
    )


@pytest.mark.parametrize("pergunta", [
    "Quantas solicitações eu tenho?",
    "Quero saber quantas solicitações tenho",
    "Qual a quantidade das minhas solicitações pendentes?",
    "Conte minhas solicitações aprovadas neste mês",
    "Qual o número de chamados que abri?",
    "Quantas ocorrências registrei em outubro?",
    "Qual o total das minhas ocorrências?",
    "Quantas ordens de serviço eu tenho?",
    "Quantas OS estão atribuídas a mim?",
    "Quantas OS concluídas tenho?",
    "Quantos feedbacks enviei?",
    "Qual o total dos meus feedbacks?",
])
@pytest.mark.parametrize("perfil", ["solicitante", "tecnico", "gestor", "administrador"])
def test_contagem_pessoal_segue_ajuda_sem_depender_do_modelo(monkeypatch, pergunta, perfil):
    modelo = SimpleNamespace(ainvoke=AsyncMock(side_effect=AssertionError("Roteador não deveria ser chamado")))
    monkeypatch.setattr(orquestrador, "roteador_estruturado", modelo)
    resultado = asyncio.run(orquestrador.rotear_orquestrador({"perfil": perfil}, pergunta))
    assert resultado.intencao == "ajuda_geral"
    assert not resultado.continua_pendente and not resultado.cadastro_em_andamento
    modelo.ainvoke.assert_not_awaited()


@pytest.mark.parametrize("pergunta,intencao", [
    ("Quantas solicitações estão pendentes?", "analytics"),
    ("Quantas solicitações minha unidade tem?", "analytics"),
    ("Qual o total de OS da minha equipe?", "analytics"),
    ("Qual a taxa de aprovação das minhas solicitações?", "analytics"),
    ("Qual a média de tempo das minhas OS?", "analytics"),
    ("Compare minhas ocorrências por mês", "analytics"),
    ("Quantas OS tenho por técnico?", "analytics"),
    ("Quantas solicitações tenho e quantas são da unidade?", "analytics"),
    ("Mostre um gráfico do total das minhas solicitações", "visualizacao"),
    ("Quantas solicitações posso criar?", "faq"),
    ("Como vejo quantas solicitações eu tenho?", "faq"),
    ("Quero registrar uma ocorrência", "ocorrencia"),
    ("Quantas solicitações eu tenho? Crie outra", "solicitacao"),
    ("Quero saber quantas solicitações tenho e atualizar uma delas", "solicitacao"),
    ("Quero ver minhas solicitações", "ajuda_geral"),
])
def test_outros_pedidos_preservam_decisao_do_roteador(monkeypatch, pergunta, intencao):
    decisao = orquestrador.DecisaoRoteamento(
        intencao=intencao, continua_pendente=False,
        cadastro_em_andamento=intencao in {"solicitacao", "ocorrencia"}, justificativa="Teste",
    )
    modelo = SimpleNamespace(ainvoke=AsyncMock(return_value=decisao))
    monkeypatch.setattr(orquestrador, "roteador_estruturado", modelo)
    resultado = asyncio.run(orquestrador.rotear_orquestrador({}, pergunta))
    assert resultado.intencao == intencao
    modelo.ainvoke.assert_awaited_once()


@pytest.fixture
def banco(monkeypatch):
    conexao = sqlite3.connect(":memory:")
    conexao.row_factory = sqlite3.Row
    conexao.executescript("""
        CREATE TABLE usuario (id INTEGER, unidade_id INTEGER, esta_ativo BOOLEAN);
        CREATE TABLE local_unidade (id INTEGER, unidade_id INTEGER, esta_ativo BOOLEAN);
        CREATE TABLE problema (id INTEGER, usuario_id INTEGER, local_unidade_id INTEGER,
            esta_ativo BOOLEAN, status INTEGER, data_criacao TEXT);
        CREATE TABLE ocorrencia (id INTEGER, usuario_id INTEGER, local_unidade_id INTEGER,
            esta_ativo BOOLEAN, data_criacao TEXT);
        CREATE TABLE ordem_servico (id INTEGER, usuario_id INTEGER, problema_id INTEGER,
            esta_ativo BOOLEAN, status_ordem_servico INTEGER, data_criacao TEXT);
        CREATE TABLE feedback (id INTEGER, usuario_id INTEGER, data_criacao TEXT);
        INSERT INTO usuario VALUES (1, 7, 1), (2, 7, 1);
        INSERT INTO local_unidade VALUES (10, 7, 1), (11, 8, 1), (12, 7, 0);
    """)
    # Cinco próprios válidos: não pode haver o limite de três das listagens.
    for indice in range(1, 6):
        data = f"2026-10-{indice:02d} 00:00:00"
        conexao.execute("INSERT INTO problema VALUES (?, 1, 10, 1, ?, ?)", (indice, indice % 4, data))
        conexao.execute("INSERT INTO ocorrencia VALUES (?, 1, 10, 1, ?)", (indice, data))
        conexao.execute("INSERT INTO ordem_servico VALUES (?, 1, ?, 1, ?, ?)", (indice, indice, indice - 1, data))
        conexao.execute("INSERT INTO feedback VALUES (?, 1, ?)", (indice, data))
    conexao.executescript("""
        INSERT INTO problema VALUES
            (6, 2, 10, 1, 0, '2026-10-02 00:00:00'),
            (7, 1, 11, 1, 0, '2026-10-02 00:00:00'),
            (8, 1, 12, 1, 0, '2026-10-02 00:00:00'),
            (9, 1, 10, 0, 0, '2026-10-02 00:00:00');
        INSERT INTO ocorrencia VALUES
            (6, 2, 10, 1, '2026-10-02 00:00:00'),
            (7, 1, 11, 1, '2026-10-02 00:00:00'),
            (8, 1, 12, 1, '2026-10-02 00:00:00'),
            (9, 1, 10, 0, '2026-10-02 00:00:00');
        INSERT INTO ordem_servico VALUES
            (6, 2, 1, 1, 0, '2026-10-02 00:00:00'),
            (7, 1, 7, 1, 0, '2026-10-02 00:00:00'),
            (8, 1, 8, 1, 0, '2026-10-02 00:00:00'),
            (9, 1, 9, 1, 0, '2026-10-02 00:00:00'),
            (10, 1, 1, 0, 0, '2026-10-02 00:00:00');
        INSERT INTO feedback VALUES (6, 2, '2026-10-02 00:00:00');
    """)

    async def executar(perfil, sql, parametros):
        valores = {chave: valor.isoformat(sep=" ") if isinstance(valor, datetime) else valor
                   for chave, valor in parametros.items()}
        return [dict(linha) for linha in conexao.execute(sql, valores)]

    monkeypatch.setattr(contagens, "obter_unidade_id", AsyncMock(return_value=7))
    monkeypatch.setattr(contagens, "executar_consulta", executar)
    yield conexao
    conexao.close()


@pytest.mark.parametrize("tipo", ["solicitacao", "ocorrencia", "ordem_servico", "feedback"])
def test_sql_conta_todos_os_proprios_validos_sem_expor_outros(banco, tipo):
    resultado = asyncio.run(contagens.contar_meus_registros(usuario("tecnico"), tipo))
    assert resultado["status"] == "SUCESSO"
    assert resultado["total"] == 5
    assert resultado["periodo"] == {"inicio": None, "fim_exclusivo": None}


@pytest.mark.parametrize("tipo", ["solicitacao", "ocorrencia", "ordem_servico", "feedback"])
def test_periodo_inclui_inicio_exclui_fim_e_zero_e_sucesso(banco, tipo):
    resultado = asyncio.run(contagens.contar_meus_registros(
        usuario("tecnico"), tipo, inicio=date(2026, 10, 2), fim=date(2026, 10, 4),
    ))
    assert resultado["total"] == 2
    vazio = asyncio.run(contagens.contar_meus_registros(usuario("tecnico"), tipo, inicio=date(2027, 1, 1)))
    assert vazio["status"] == "SUCESSO" and vazio["total"] == 0


@pytest.mark.parametrize("tipo,situacao,total", [
    ("solicitacao", "PENDENTE", 1), ("solicitacao", "APROVADA", 1),
    ("solicitacao", "REPROVADA", 2), ("solicitacao", "CONCLUIDA", 1),
    ("ordem_servico", "ABERTA", 4), ("ordem_servico", "CONCLUIDA", 1),
    ("ordem_servico", "EM_ANDAMENTO", 1), ("ordem_servico", "ATRASADA", 1),
])
def test_filtra_situacao_real_sem_mudar_escopo(banco, tipo, situacao, total):
    resultado = asyncio.run(contagens.contar_meus_registros(usuario("tecnico"), tipo, situacao=situacao))
    assert resultado["total"] == total


def test_total_pessoal_inclui_registros_anteriores_a_janela_das_listagens(banco):
    banco.execute("INSERT INTO problema VALUES (20, 1, 10, 1, 0, '2020-01-01 00:00:00')")
    resultado = asyncio.run(contagens.contar_meus_registros(usuario(), "solicitacao"))
    assert resultado["total"] == 6


def test_os_propria_significa_atribuida_ao_usuario_e_nao_autoria_do_problema(banco):
    banco.execute("INSERT INTO ordem_servico VALUES (20, 1, 6, 1, 0, '2026-10-01 00:00:00')")
    resultado = asyncio.run(contagens.contar_meus_registros(usuario("tecnico"), "ordem_servico"))
    assert resultado["total"] == 6


@pytest.mark.parametrize("tipo", ["ocorrencia", "ordem_servico"])
def test_solicitante_nao_ganha_acesso_a_registros_restritos(monkeypatch, tipo):
    unidade = AsyncMock()
    monkeypatch.setattr(contagens, "obter_unidade_id", unidade)
    resultado = asyncio.run(contagens.contar_meus_registros(usuario(), tipo))
    assert resultado["status"] == "ACESSO_NEGADO"
    unidade.assert_not_awaited()


@pytest.mark.parametrize("argumentos", [
    {"tipo_registro": "usuario"},
    {"tipo_registro": "ocorrencia", "situacao": "PENDENTE"},
    {"tipo_registro": "feedback", "situacao": "CONCLUIDA"},
    {"tipo_registro": "solicitacao", "inicio": date(2026, 10, 1), "fim": date(2026, 10, 1)},
    {"tipo_registro": "solicitacao", "inicio": datetime(2026, 10, 1)},
])
def test_argumentos_invalidos_nao_consultam_banco(monkeypatch, argumentos):
    unidade = AsyncMock()
    monkeypatch.setattr(contagens, "obter_unidade_id", unidade)
    resultado = asyncio.run(contagens.contar_meus_registros(usuario("tecnico"), **argumentos))
    assert resultado["status"] == "ERRO_VALIDACAO"
    unidade.assert_not_awaited()


def test_falha_de_banco_nao_e_convertida_em_zero(monkeypatch):
    monkeypatch.setattr(contagens, "obter_unidade_id", AsyncMock(return_value=7))
    monkeypatch.setattr(contagens, "executar_consulta", AsyncMock(side_effect=RuntimeError("indisponível")))
    resultado = asyncio.run(contagens.contar_meus_registros(usuario(), "solicitacao"))
    assert resultado["status"] == "ERRO_FERRAMENTA" and "total" not in resultado


@pytest.mark.parametrize("campo", ["usuario_id", "unidade_id", "runtime", "limite", "local"])
def test_modelo_nao_injeta_identidade_ou_filtros_ignorados(campo):
    with pytest.raises(ValidationError):
        _ContagemPessoal.model_validate({"tipo_registro": "solicitacao", campo: {"usuario_id": 2}})


@pytest.mark.parametrize("perfil", ["solicitante", "tecnico", "gestor", "administrador"])
def test_ferramenta_disponivel_na_ajuda_de_cada_perfil(monkeypatch, perfil):
    monkeypatch.setattr(ajuda_geral, "create_agent", lambda **kwargs: kwargs)
    agente = ajuda_geral.criar_agente_ajuda_geral(None, "teste", perfil=perfil)
    assert sum(t.name == "contar_meus_registros" for t in agente["tools"]) == 1


def test_pedido_pessoal_pausa_cadastro_e_gera_evidencia_do_total(banco, monkeypatch):
    texto = "Quantas solicitações eu tenho?"
    contexto = {"usuario": usuario(), "session_id": "sessao", "turno_id": "turno",
                "mensagem_atual": texto, "imagens": []}
    estado = {"perfil": "solicitante", "messages": [HumanMessage(content=texto)],
              "solicitacao_pendente": {"id": "rascunho", "versao": 1,
                                       "status_fluxo": "aguardando_confirmacao", "pausado": False}}
    atualizar = AsyncMock(return_value=True)
    monkeypatch.setattr(continuacoes, "atualizar_rascunho_solicitacao", atualizar)

    async def executar(_estado, *, context):
        retorno = await contar_meus_registros.coroutine("solicitacao", SimpleNamespace(context=context))
        return {"structured_response": FAQResultado(agente="ajuda_geral", status="SUCESSO",
                                                    resposta=f"Você tem {retorno['total']} solicitações."),
                "messages": [AIMessage(content="", tool_calls=[{
                    "id": "contagem-1", "name": "contar_meus_registros", "args": {"tipo_registro": "solicitacao"},
                }]), ToolMessage(content=json.dumps(retorno), tool_call_id="contagem-1")]}

    monkeypatch.setattr(nos, "ajuda_geral_solicitante", SimpleNamespace(ainvoke=executar))
    runtime = SimpleNamespace(context=contexto)
    decisao = asyncio.run(nos.supervisionar(estado, runtime))
    assert decisao["intencao"] == "ajuda_geral"
    assert decisao["solicitacao_pendente"]["pausado"]
    resultado = asyncio.run(nos.executar_ajuda_geral({**estado, **decisao}, runtime))
    assert resultado["erro"] is None
    assert resultado["resposta_especialista"] == "Você tem 5 solicitações."
    assert json.loads(resultado["evidencias"][0])["resultado"]["total"] == 5
    assert not contexto.get("operacoes_pendentes")
