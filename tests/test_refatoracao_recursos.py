"""Regras compartilhadas com políticas distintas preservadas por domínio."""

import asyncio
from datetime import date, datetime, timezone
import importlib
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from pydantic import ValidationError

from app.core import data_iso_banco, inicio_periodo_listagem
from app.core.tabelas import escapar_celula
from app.schemas.cadastros import CriarEventoEntrada
from app.services.indicadores.gerais import ConfiguracaoDatabricksAusente, ErroDatabricks, TimeoutConsultaDatabricks


@pytest.mark.parametrize('hoje,esperado', [(date(2026,5,31),date(2026,2,28)),(date(2024,5,31),date(2024,2,29)),(date(2026,1,31),date(2025,10,31)),(date(2026,3,30),date(2025,12,30))])
def test_tres_meses_respeitam_calendario_e_ano_bissexto(hoje, esperado):
    assert inicio_periodo_listagem(hoje) == esperado


@pytest.mark.parametrize('valor', [None, '', '2026-01-01', 0, True])
def test_data_obrigatoria_nao_aceita_nulo_ou_coercao(valor):
    with pytest.raises(ValueError):
        data_iso_banco(valor)


def test_data_opcional_e_datetime_preservam_politica_da_listagem():
    assert data_iso_banco(None, permitir_nulo=True) is None
    assert data_iso_banco(datetime(2026,1,2,3,4,tzinfo=timezone.utc)) == '2026-01-02'


@pytest.mark.parametrize('texto,esperado', [('a|b','a&#124;b'),('[x](https://example.com)','&#91;x&#93;(https://example.com)'),('<img src=x>','&lt;img src=x&gt;'),('a\r\nb\rc','a<br>b<br>c'),('*negrito*','&#42;negrito&#42;'),(0,'0')])
def test_celulas_nao_criam_links_colunas_ou_html(texto, esperado):
    assert escapar_celula(texto, ausente='Ausente') == esperado


def test_textos_de_ausencia_dos_dois_dominios_sao_preservados():
    from app.tools.ocorrencias.utilitarios import _celula as ocorrencia
    from app.tools.ordensServico.utilitarios import _celula as ordem
    assert ocorrencia(None) == 'Não informado'
    assert ordem(None) == 'Não informada'


@pytest.mark.parametrize('dominio', ['ocorrencia','problema','ordem_servico'])
@pytest.mark.parametrize('falha,status', [(TimeoutConsultaDatabricks,'TIMEOUT'),(ConfiguracaoDatabricksAusente,'ERRO_FERRAMENTA'),(ErroDatabricks,'ERRO_FERRAMENTA'),(RuntimeError,'ERRO_FERRAMENTA')])
def test_falhas_dos_tres_indicadores_preservam_resultado(monkeypatch, dominio, falha, status):
    modulo = importlib.import_module('app.services.indicadores.' + dominio)
    executor = AsyncMock(side_effect=falha('simulada'))
    monkeypatch.setattr(modulo, 'executar_consulta', executor)
    monkeypatch.setattr(modulo, 'registrador', Mock())
    resultado = asyncio.run(modulo._consultar('SELECT 1', {'unidade_id':7}))
    assert resultado['status'] == status
    assert executor.await_count == 1
    assert 'simulada' not in resultado['mensagem']


@pytest.mark.parametrize('inicio,fim', [(date(2026,1,1),date(2026,1,1)),(date(2026,2,1),date(2026,1,1)),(datetime(2026,1,1),date(2026,2,1)),('2026-01-01',date(2026,2,1))])
@pytest.mark.parametrize('dominio', ['ocorrencia','problema','ordem_servico'])
def test_periodo_invalido_nao_chega_ao_warehouse(monkeypatch, dominio, inicio, fim):
    modulo = importlib.import_module('app.services.indicadores.' + dominio)
    executor = AsyncMock()
    monkeypatch.setattr(modulo,'executar_consulta',executor)
    nome = {'ocorrencia':'obter_total_ocorrencias','problema':'obter_total_solicitacoes','ordem_servico':'obter_total_os'}[dominio]
    resultado = asyncio.run(getattr(modulo,nome)(inicio,fim,unidade_id=7))
    assert resultado['status'] == 'ERRO_VALIDACAO'
    executor.assert_not_awaited()
