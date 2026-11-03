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
        """Executa a etapa executar no escopo de tracing. Usado pelo fluxo de observability."""
        with tracing_context(enabled=False):
            return await funcao(*args, **kwargs)
    return executar


class SomenteMetricasMiddleware:
    """Aplica a política também ao contexto de cada requisição ASGI."""

    def __init__(self, app):
        """Inicializa os atributos da instância para as operações da classe. Usado pelo fluxo de observability."""
        self.app = app

    async def __call__(self, scope, receive, send):
        """Adapta o callback __call__ às regras e ao contexto desta classe. Usado pelo fluxo de observability."""
        with tracing_context(enabled=False):
            await self.app(scope, receive, send)
