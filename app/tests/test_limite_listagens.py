"""Recorte das consultas exibidas no chat."""

import asyncio
import json
from datetime import date
from importlib import import_module
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.services.ocorrencias import buscarOcorrencias as ocorrencias
from app.services.ordensServico import buscarOrdensServico as ordens
from app.services.solicitacoes import buscarSolicitacao as solicitacoes
from app.agents.agentsResult import FAQResultado
from app.graph import nos


HOJE = date(2026, 10, 25)
juiz = import_module("app.agents.juiz")


@pytest.mark.parametrize("modulo, consulta, coluna", [
    (ocorrencias, "consultar_minhas_ocorrencias", "ocorrencia"),
    (solicitacoes, "listar_minhas_solicitacoes", "p"),
    (ordens, "consultar_minhas_ordens_servico", "os"),
    (ordens, "consultar_todas_ordens_servico", "os"),
])
def test_listagens_restringem_periodo_e_tres_mais_recentes(
    monkeypatch, modulo, consulta, coluna,
):
    banco = AsyncMock(return_value=[])
    monkeypatch.setattr(modulo, "executar_consulta", banco)
    monkeypatch.setattr(modulo, "data_atual", lambda: HOJE)
    usuario = SimpleNamespace(tipo_acesso="gestor", usuario_id=7)

    resultado = asyncio.run(getattr(modulo, consulta)(usuario))

    sql, parametros = banco.await_args.args[1:3]
    assert f"{coluna}.data_criacao >= :inicio" in sql
    assert f"{coluna}.data_criacao < :fim_exclusivo" in sql
    assert f"ORDER BY {coluna}.data_criacao DESC, {coluna}.id DESC" in sql
    assert "LIMIT 3" in sql
    assert parametros["inicio"] == date(2026, 7, 25)
    assert parametros["fim_exclusivo"] == date(2026, 10, 26)
    assert resultado["status"] == "SEM_RESULTADO"
    assert resultado["orientacao"]


def test_busca_filtrada_de_ordens_limita_resultados_sem_alterar_periodo_expresso(monkeypatch):
    banco = AsyncMock(return_value=[])
    monkeypatch.setattr(ordens, "executar_consulta", banco)
    usuario = SimpleNamespace(tipo_acesso="tecnico", usuario_id=7)

    resultado = asyncio.run(ordens.buscar_ordens_servico(
        usuario, prioridade="ALTA",
        data_criacao_inicio=date(2026, 1, 1),
        data_criacao_fim=date(2026, 2, 28),
    ))

    sql, parametros = banco.await_args.args[1:3]
    assert "LIMIT 3" in sql
    assert "ORDER BY os.data_criacao DESC, os.id DESC" in sql
    assert parametros["data_criacao_inicio"] == date(2026, 1, 1)
    assert parametros["data_criacao_fim_exclusivo"] == date(2026, 3, 1)
    assert resultado["orientacao"]


def test_pendencias_do_gestor_mostram_cinco_mais_recentes(monkeypatch):
    banco = AsyncMock(return_value=[])
    monkeypatch.setattr(solicitacoes, "executar_consulta", banco)
    monkeypatch.setattr(solicitacoes, "data_atual", lambda: HOJE)
    usuario = SimpleNamespace(tipo_acesso="gestor", usuario_id=7)

    resultado = asyncio.run(solicitacoes.listar_solicitacoes_pendentes(usuario))

    sql, parametros = banco.await_args.args[1:3]
    assert "p.status = 0" in sql
    assert "ORDER BY p.data_criacao DESC, p.id DESC LIMIT 5" in sql
    assert parametros["inicio"] == date(2026, 7, 25)
    assert parametros["fim_exclusivo"] == date(2026, 10, 26)
    assert "Solicitações abertas" in resultado["orientacao"]


def test_orientacao_da_consulta_atual_eh_exibida_uma_vez_no_final(monkeypatch):
    anterior = json.dumps({"ferramenta": "listar_minhas_ocorrencias",
                           "status_operacao": "SUCESSO",
                           "resultado": {"orientacao": "Orientação antiga."}})
    atual = json.dumps({"ferramenta": "listar_minhas_solicitacoes",
                        "status_operacao": "SUCESSO",
                        "resultado": {"orientacao": "Veja Minhas solicitações no app."}})
    resposta = FAQResultado(
        agente="ajuda_geral", status="SUCESSO",
        resposta="Aqui estão os registros.\n\nVeja Minhas solicitações no app.",
    )
    monkeypatch.setattr(nos, "executar_com_evidencias", AsyncMock(return_value=(
        {"structured_response": resposta}, [anterior, atual],
    )))

    resultado = asyncio.run(nos.executar_ajuda_geral(
        {"perfil": "tecnico", "evidencias": [anterior]},
        SimpleNamespace(context={}),
    ))

    assert resultado["resposta_especialista"].endswith("Veja Minhas solicitações no app.")
    assert resultado["resposta_especialista"].count("Veja Minhas solicitações no app.") == 1
    assert "Orientação antiga" not in resultado["resposta_especialista"]


def test_orientacao_nao_aparece_quando_a_consulta_falha():
    falha = json.dumps({"ferramenta": "listar_minhas_ocorrencias",
                        "status_operacao": "ERRO_FERRAMENTA",
                        "resultado": {"orientacao": "Veja mais no app."}})
    assert nos._anexar_orientacao_consulta("Não foi possível consultar.", [falha]) == (
        "Não foi possível consultar."
    )


def test_juiz_recebe_tabela_inteira_sem_repetir_linhas_estruturadas():
    evidencia = json.dumps({
        "ferramenta": "listar_minhas_ocorrencias",
        "status_operacao": "SUCESSO",
        "resultado": {
            "status": "SUCESSO",
            "ocorrencias": [{"descricao": "x" * 700}] * 3,
            "tabela_markdown": "| Título |\n| --- |\n" + "| dado |\n" * 300,
        },
    }, ensure_ascii=False)
    assert len(evidencia) > 4000

    preparada = juiz._evidencias_jev([evidencia])[0]

    assert isinstance(preparada, dict)
    assert preparada["status_operacao"] == "SUCESSO"
    assert preparada["resultado"]["tabela_markdown"].endswith("| dado |\n")
    assert "ocorrencias" not in preparada["resultado"]
