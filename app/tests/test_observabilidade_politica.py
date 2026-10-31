"""Política de conteúdo, isolamento de contexto e configuração do monitoramento."""

import asyncio
import json
from pathlib import Path
from unittest.mock import Mock

from fastapi import FastAPI
from fastapi.testclient import TestClient
from langsmith import Client, traceable, tracing_context
from langsmith.utils import get_env_var, tracing_is_enabled
import pytest
import yaml

from app.observability.tracing import (
    SomenteMetricasMiddleware, configurar_somente_metricas, somente_metricas,
)

RAIZ = Path(__file__).resolve().parents[2]


def test_politica_sobrescreve_flags_ativadas_e_cache(monkeypatch):
    nomes = ("LANGSMITH_TRACING", "LANGSMITH_TRACING_V2", "LANGCHAIN_TRACING_V2", "LANGCHAIN_TRACING")
    for n in nomes: monkeypatch.setenv(n, "true")
    get_env_var.cache_clear()
    assert tracing_is_enabled()
    configurar_somente_metricas()
    assert tracing_is_enabled() is False
    import os
    assert all(os.environ[n] == "false" for n in nomes)


@pytest.mark.parametrize("falha", [False, True])
def test_entrada_direta_nao_envia_traces_nem_herda_pai(falha):
    cliente = Mock(spec=Client)
    @traceable(client=cliente)
    async def modelo(texto):
        assert tracing_is_enabled() is False
        if falha: raise ValueError("Falha controlada")
        return texto
    @somente_metricas
    async def entrada(): return await modelo("dado-privado")
    async def executar():
        with tracing_context(enabled=True):
            if falha:
                with pytest.raises(ValueError): await entrada()
            else: assert await entrada() == "dado-privado"
            assert tracing_is_enabled() is True
    asyncio.run(executar())
    cliente.create_run.assert_not_called()
    cliente.update_run.assert_not_called()


def test_middleware_desabilita_tracing_na_requisicao():
    api = FastAPI()
    api.add_middleware(SomenteMetricasMiddleware)
    @api.get("/teste")
    async def endpoint(): return {"tracing": tracing_is_enabled()}
    with tracing_context(enabled=True):
        assert TestClient(api).get("/teste").json() == {"tracing": False}
        assert tracing_is_enabled() is True


def test_configuracao_prometheus_compose_e_dashboard_consistentes():
    prom = yaml.safe_load((RAIZ / "observability/prometheus.yml").read_text(encoding="utf-8"))
    compose = yaml.safe_load((RAIZ / "compose.observability.yml").read_text(encoding="utf-8"))
    regras = yaml.safe_load((RAIZ / "observability/rules/visualizacoes.yml").read_text(encoding="utf-8"))
    assert "/etc/prometheus/rules/*.yml" in prom["rule_files"]
    assert "./observability/rules:/etc/prometheus/rules:ro" in compose["services"]["prometheus"]["volumes"]
    assert prom["scrape_configs"][0]["metrics_path"] == "/api/v1/metrics"
    nomes = {r["record"] for g in regras["groups"] for r in g["rules"]}
    assert len(nomes) == 3
    for g in regras["groups"]:
        for r in g["rules"]:
            assert 'job="fixa-api"' in r["expr"]
            assert "user_id" not in r["expr"] and "session_id" not in r["expr"]
    dashboard = json.loads((RAIZ / "observability/grafana/dashboards/fixa-observability.json").read_text(encoding="utf-8"))
    ids = [p["id"] for p in dashboard["panels"]]
    assert len(ids) == len(set(ids)) == 17
    assert set(range(1, 11)) <= set(ids)
    for p in dashboard["panels"]:
        assert "??" not in p["title"]
        if p["type"] != "row": assert p["datasource"]["uid"] == "prometheus"
    consultas = " ".join(t["expr"] for p in dashboard["panels"] for t in p.get("targets", []))
    assert all(n in consultas for n in nomes)
    assert "ERRO_FERRAMENTA|TIMEOUT|RESULTADO_TRUNCADO" in consultas
