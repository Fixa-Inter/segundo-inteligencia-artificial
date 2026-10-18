"""Regras de acesso e paginação sem conectar aos bancos."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.schemas import UsuarioContexto
from app.services.ajuda_geral import consultas


def criar_usuario(perfil="solicitante"):
    return UsuarioContexto(
        access_token="teste", usuario_id=1, nome_completo="Teste",
        email="teste@exemplo.com", tipo_acesso=perfil, cnpj_endereco="12345678000190",
    )


@pytest.mark.parametrize("colecao", ["ocorrencia", "ordem_servico", "tarefa", "equipamento"])
def test_solicitante_nao_consulta_colecao_restrita(monkeypatch, colecao):
    obter_unidade = AsyncMock()
    monkeypatch.setattr(consultas, "obter_unidade_id", obter_unidade)
    resultado = asyncio.run(consultas.buscar_semanticamente(criar_usuario(), colecao, "Texto", 5))
    assert resultado["status"] == "ACESSO_NEGADO"
    obter_unidade.assert_not_awaited()


@pytest.mark.parametrize("limite", [0, -1, 11, True, "5"])
def test_limite_invalido_impede_consulta(monkeypatch, limite):
    obter_unidade = AsyncMock()
    monkeypatch.setattr(consultas, "obter_unidade_id", obter_unidade)
    resultado = asyncio.run(consultas.buscar_semanticamente(criar_usuario(), "problema", "Texto", limite))
    assert resultado["status"] == "ERRO_VALIDACAO"
    obter_unidade.assert_not_awaited()


@pytest.mark.parametrize("colecao,unidade", [("evento", 7), ("problema", 8)])
def test_cursor_nao_transita_entre_unidades_colecoes(colecao, unidade):
    cursor = consultas._codificar_cursor("problema", 7, 30)
    with pytest.raises(ValueError):
        consultas._decodificar_cursor(cursor, colecao, unidade)


def test_registro_outra_unidade_rejeitado():
    ponto = SimpleNamespace(payload={"entidade_id": 1, "unidade_id": 8,
                                     "esta_ativo": True, "texto": "Registro"})
    with pytest.raises(RuntimeError, match="fora da unidade"):
        consultas._registro("problema", ponto, 7)


def test_solicitante_sem_problemas_nao_consulta_vetor(monkeypatch):
    monkeypatch.setattr(consultas, "obter_unidade_id", AsyncMock(return_value=7))
    monkeypatch.setattr(consultas, "executar_consulta", AsyncMock(return_value=[]))
    vetor = AsyncMock()
    monkeypatch.setattr(consultas, "gerar_vetor_operacional", vetor)
    resultado = asyncio.run(consultas.buscar_semanticamente(criar_usuario(), "problema", "Texto", 5))
    assert resultado["status"] == "SEM_RESULTADO"
    vetor.assert_not_awaited()


def test_problemas_solicitante_filtrados_usuario_unidade(monkeypatch):
    consulta = AsyncMock(return_value=[{"id": 3}, {"id": 4}])
    monkeypatch.setattr(consultas, "executar_consulta", consulta)
    filtro = asyncio.run(consultas._filtro_usuario(criar_usuario(), "problema", 7))
    assert filtro.match.any == [3, 4]
    argumentos = consulta.await_args.args
    assert argumentos[2] == {"usuario_id": 1, "unidade_id": 7}
    assert "p.usuario_id = :usuario_id" in argumentos[1]
    assert "local.unidade_id = :unidade_id" in argumentos[1]
