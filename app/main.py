from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.clients.mongo import validar_config_mongo
from app.memory.persistencia.garantir_indice import garantir_indice_persistencia
from app.memory.vectorSearch.garantir_indice import garantir_indice_historico


@asynccontextmanager
async def lifespan(app: FastAPI):
    validar_config_mongo()
    await garantir_indice_persistencia()
    await garantir_indice_historico()
    yield

app = FastAPI(
    lifespan=lifespan,
    title="Segundo Inteligência Artificial",
    description="API da Plataforma de Manutenção FIXA com IA.",
    version="0.1.0",
)

app.include_router(
    api_router,
    prefix="/api/v1",
)
