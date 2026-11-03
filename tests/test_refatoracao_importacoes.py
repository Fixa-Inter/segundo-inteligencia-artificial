"""Interfaces públicas em processos limpos, sem rede e sem depender da ordem."""

import ast
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


RAIZ = Path(__file__).resolve().parents[1]
PACOTES = ['app.core', 'app.schemas', 'app.services', 'app.tools', 'app.memory', 'app.agents', 'app.guardrails', 'app.graph', 'app.api', 'app.observability']


@pytest.mark.parametrize('ordem', [PACOTES, list(reversed(PACOTES)), PACOTES[4:] + PACOTES[:4]], ids=['camadas', 'inversa', 'memoria-primeiro'])
def test_importar_interfaces_nao_inicializa_grafo_modelos_ou_bancos(ordem):
    """Importações dos namespaces devem ser leves e não iniciar recursos externos."""
    codigo = '''
import importlib, json, socket, sys
def negar(*args, **kwargs): raise AssertionError('Importacao tentou acessar a rede')
socket.socket.connect = negar
for nome in json.loads(sys.argv[1]): importlib.import_module(nome)
assert 'app.graph.fluxo' not in sys.modules
assert 'app.core.clients.modelos' not in sys.modules
assert 'app.agents.registro' not in sys.modules
'''
    resultado = subprocess.run([sys.executable, '-c', codigo, json.dumps(ordem)], cwd=RAIZ, capture_output=True, text=True, timeout=30)
    assert resultado.returncode == 0, resultado.stdout + resultado.stderr


def test_todas_exportacoes_resolvem_em_processo_limpo_sem_ciclos():
    """Resolve funções/classes/constantes de todas as fachadas sem abrir conexões."""
    pacotes = sorted('.'.join(p.parent.relative_to(RAIZ).parts) for p in (RAIZ/'app').rglob('__init__.py') if 'tests' not in p.parts)
    codigo = '''
import importlib, json, socket, sys
def negar(*args, **kwargs): raise AssertionError('Resolucao tentou acessar a rede')
socket.socket.connect = negar
for nome in json.loads(sys.argv[1]):
    modulo = importlib.import_module(nome)
    for simbolo in getattr(modulo, '__all__', []): getattr(modulo, simbolo)
'''
    ambiente = {**os.environ, 'OPENAI_API_KEY': 'sk-local-import-test'}
    resultado = subprocess.run([sys.executable, '-c', codigo, json.dumps(pacotes)], cwd=RAIZ, env=ambiente, capture_output=True, text=True, timeout=60)
    assert resultado.returncode == 0, resultado.stdout + resultado.stderr


def test_core_nao_importa_grafo_agentes_servicos_ou_ferramentas():
    """Regras comuns não podem voltar a depender da orquestração de aplicação."""
    proibidas = []
    for arquivo in (RAIZ/'app/core').rglob('*.py'):
        for no in ast.walk(ast.parse(arquivo.read_text(encoding='utf-8-sig'))):
            if isinstance(no, ast.ImportFrom) and (no.module or '').startswith(('app.graph', 'app.agents', 'app.services', 'app.tools')):
                proibidas.append(f'{arquivo.relative_to(RAIZ)}:{no.lineno}')
    assert proibidas == []


def test_fachada_observa_substituicao_no_modulo_proprietario(monkeypatch):
    """Evita congelar referências de modelo/cliente ao centralizar importações."""
    import app.agents as agentes
    import app.agents.modelos as modelos
    substituto = object()
    monkeypatch.setattr(modelos, 'llm_especialista', substituto)
    assert agentes.llm_especialista is substituto
