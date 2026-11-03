"""Caracterização dos cadastros: referência executada no código anterior."""

import asyncio
import importlib
import json
from pathlib import Path

import httpx
import pytest

from app.schemas.cadastros import CriarEventoEntrada, CriarOcorrenciaEntrada, CriarSolicitacaoEntrada


# Resultados e requisições originais em 132 combinações de serviço/status/corpo.
CENARIOS = json.loads((Path(__file__).parent / 'fixtures/cadastros_antes_refatoracao.json').read_text(encoding='utf-8'))
DOMINIOS = {
    'solicitacao': ('solicitacoes.criarSolicitacao', CriarSolicitacaoEntrada),
    'ocorrencia': ('ocorrencias.criarOcorrencia', CriarOcorrenciaEntrada),
    'evento': ('eventos.criarEvento', CriarEventoEntrada),
}


@pytest.mark.parametrize('cenario', CENARIOS, ids=[f"{c['dominio']}-{c['http_status']}-{i}" for i, c in enumerate(CENARIOS)])
def test_cadastro_preserva_resultado_payload_bearer_e_envio_unico(monkeypatch, cenario):
    """Verifica respostas completas, transporte e ausência de repetição do POST."""
    nome_modulo, contrato = DOMINIOS[cenario['dominio']]
    modulo = importlib.import_module('app.services.' + nome_modulo)
    corpo = cenario['corpo']
    resposta = httpx.Response(cenario['http_status'], text=corpo) if isinstance(corpo, str) else httpx.Response(cenario['http_status'], json=corpo)
    chamadas, opcoes = [], []

    class ClienteSimulado:
        """Captura o transporte sem rede e sem alterar o comportamento do serviço."""

        def __init__(self, **kwargs):
            opcoes.append(kwargs)

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def post(self, url, **kwargs):
            chamadas.append({'url': url, **kwargs})
            return resposta

    monkeypatch.setattr(modulo, 'FIXA_URL_BASE_API', 'https://fixa.example/')
    monkeypatch.setattr(modulo.httpx, 'AsyncClient', ClienteSimulado)
    metodo = getattr(modulo, 'adicionar_' + cenario['dominio'])
    resultado = asyncio.run(metodo(contrato.model_validate(cenario['dados']), 'token-local', **cenario['kwargs']))
    assert resultado == cenario['resultado']
    assert chamadas == cenario['requests']
    assert opcoes == cenario['client_options']
    assert len(chamadas) == 1


@pytest.mark.parametrize('dominio', sorted(DOMINIOS))
@pytest.mark.parametrize('falha', [httpx.ConnectError, httpx.ReadTimeout])
def test_erro_de_transporte_nao_declara_sucesso_nem_reenvia(monkeypatch, dominio, falha):
    """Uma gravação potencialmente enviada permanece indeterminada, sem retry."""
    cenario = next(c for c in CENARIOS if c['dominio'] == dominio)
    nome, contrato = DOMINIOS[dominio]
    modulo = importlib.import_module('app.services.' + nome)
    chamadas = []

    class ClienteComFalha:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def post(self, *args, **kwargs):
            chamadas.append(kwargs)
            raise falha('Falha de transporte simulada')

    monkeypatch.setattr(modulo, 'FIXA_URL_BASE_API', 'https://fixa.example/')
    monkeypatch.setattr(modulo.httpx, 'AsyncClient', lambda **kwargs: ClienteComFalha())
    resultado = asyncio.run(getattr(modulo, 'adicionar_' + dominio)(contrato.model_validate(cenario['dados']), 'token-local', **cenario['kwargs']))
    assert resultado['status'] == 'RESULTADO_INDETERMINADO'
    assert len(chamadas) == 1
