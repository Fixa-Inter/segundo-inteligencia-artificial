from contextlib import AsyncExitStack, asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.observability.tracing import SomenteMetricasMiddleware

from app.api.router import api_router
from app.core.clients.mongo import fechar_cliente_mongo, iniciar_cliente_mongo
from app.core.clients.qdrant import fechar_cliente_qdrant, iniciar_cliente_qdrant
from app.core.clients.databricks import fechar_cliente_databricks
from app.core.clients.postgres import fechar_conexoes_postgres
from app.memory.persistencia.garantir_indice import garantir_indice_persistencia
from app.memory.vectorSearch.garantir_indice import (
    garantir_indice_historico,
    garantir_indices_operacionais,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncExitStack() as recursos:
        recursos.push_async_callback(fechar_conexoes_postgres)
        recursos.push_async_callback(fechar_cliente_databricks)
        recursos.push_async_callback(fechar_cliente_mongo)
        recursos.push_async_callback(fechar_cliente_qdrant)
        iniciar_cliente_mongo()
        iniciar_cliente_qdrant()
        await garantir_indice_persistencia()
        await garantir_indice_historico()
        await garantir_indices_operacionais()
        yield

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
