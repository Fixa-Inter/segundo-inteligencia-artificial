"""Política da aplicação: métricas agregadas, sem exportar conteúdo ao LangSmith."""

import os
from functools import wraps

from langsmith import tracing_context
from langsmith.utils import get_env_var


def configurar_somente_metricas() -> None:
    """Aplica a política no processo, inclusive sobre flags carregadas do .env."""
    for nome in (
        "LANGSMITH_TRACING", "LANGSMITH_TRACING_V2", "LANGCHAIN_TRACING_V2", "LANGCHAIN_TRACING",
    ):
        os.environ[nome] = "false"
    get_env_var.cache_clear()


def somente_metricas(funcao):
    """Impede herdar tracing habilitado em entradas programáticas assíncronas."""
    @wraps(funcao)
    async def executar(*args, **kwargs):
        with tracing_context(enabled=False):
            return await funcao(*args, **kwargs)
    return executar


class SomenteMetricasMiddleware:
    """Aplica a política também ao contexto de cada requisição ASGI."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        with tracing_context(enabled=False):
            await self.app(scope, receive, send)
