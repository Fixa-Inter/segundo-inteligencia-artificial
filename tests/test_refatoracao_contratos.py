"""Compara contratos públicos com capturas feitas antes da refatoração."""

import importlib
import json
from pathlib import Path

import pytest

from app.main import app


# Captura estática do OpenAPI e dos schemas enviados ao LLM, sem credenciais.
REFERENCIA = json.loads((Path(__file__).parent / 'fixtures/contratos_antes_refatoracao.json').read_text(encoding='utf-8'))


def test_openapi_preserva_rotas_campos_descricoes_e_status():
    """Detecta alterações no contrato HTTP, inclusive documentação/validação."""
    assert app.openapi() == REFERENCIA['openapi']


@pytest.mark.parametrize('chave', sorted(REFERENCIA['tools']))
def test_argumentos_das_ferramentas_preservam_contrato_do_modelo(chave):
    """Mantém nomes, tipos, limites e obrigatoriedade dos argumentos originais."""
    module_name, symbol = chave.split('::')
    tool = getattr(importlib.import_module(module_name), symbol)
    assert tool.tool_call_schema.model_json_schema() == REFERENCIA['tools'][chave]


@pytest.mark.parametrize('chave', sorted(REFERENCIA['prompts']))
def test_instrucoes_dos_agentes_preservam_texto_original_inclusive_espacos(chave):
    """Evita mudar a entrada do LLM ao reorganizar imports e comentar o código."""
    module_name, symbol = chave.split('::')
    recurso = getattr(importlib.import_module(module_name), symbol)
    texto = recurso() if callable(recurso) else recurso
    assert texto == REFERENCIA['prompts'][chave]


@pytest.mark.parametrize('classe', ['CriarSolicitacaoEntrada', 'CriarOcorrenciaEntrada', 'CriarEventoEntrada'])
def test_caminho_antigo_de_cadastro_reexporta_a_mesma_classe(classe):
    """Chamadores legados e serviços novos usam a mesma classe e validação."""
    antiga = getattr(importlib.import_module('app.tools.toolsRequest'), classe)
    canonica = getattr(importlib.import_module('app.schemas.cadastros'), classe)
    assert antiga is canonica


@pytest.mark.parametrize('classe', ['FAQResultado', 'IndicadoresResultado', 'RetornoUsuarioResultado', 'SolicitacaoOcorrenciaResultado', 'VisualizacaoResultado'])
def test_caminho_antigo_de_resultado_reexporta_a_mesma_classe(classe):
    """Mantém identidade dos contratos usados por agentes e pelo grafo."""
    antiga = getattr(importlib.import_module('app.agents.agentsResult'), classe)
    canonica = getattr(importlib.import_module('app.schemas.resultados_agentes'), classe)
    assert antiga is canonica
