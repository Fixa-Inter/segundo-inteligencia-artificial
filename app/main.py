from contextlib import AsyncExitStack, asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.observability import SomenteMetricasMiddleware
from app.api import api_router
from app.core.clients import (
    fechar_cliente_mongo,
    iniciar_cliente_mongo,
    fechar_cliente_qdrant,
    iniciar_cliente_qdrant,
    fechar_cliente_databricks,
    fechar_conexoes_postgres,
)
from app.memory.persistencia import garantir_indice_persistencia
from app.memory.vectorSearch import (
    garantir_indice_faq,
    garantir_indice_historico,
    garantir_indices_operacionais,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa clientes/índices e garante encerramento dos recursos, inclusive em falha de startup. Usado pelo fluxo de app."""
    async with AsyncExitStack() as recursos:
        recursos.push_async_callback(fechar_conexoes_postgres)
        recursos.push_async_callback(fechar_cliente_databricks)
        recursos.push_async_callback(fechar_cliente_mongo)
        recursos.push_async_callback(fechar_cliente_qdrant)
        iniciar_cliente_mongo()
        iniciar_cliente_qdrant()
        await garantir_indice_persistencia()
        await garantir_indice_historico()
        await garantir_indice_faq()
        await garantir_indices_operacionais()
        yield

# app: Recurso compartilhado de app usado pelas funções deste módulo e pela interface pública.
app = FastAPI(
    lifespan=lifespan,
    title="Segundo Inteligência Artificial",
    description="API da Plataforma de Manutenção FIXA com IA.",
    version="0.1.0",
)
app.add_middleware(SomenteMetricasMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    api_router,
    prefix="/api/v1",
)
