from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from app.memory.vectorSearch.garantir_collections import garantir_collections

from app.api.router import api_router
from app.core.clients.mongo import validar_config_mongo
from app.core.clients.postgres import fechar_conexoes_postgres
from app.memory.persistencia.garantir_indice import garantir_indice_persistencia
from app.memory.vectorSearch.garantir_indice import (
    garantir_indice_historico,
    garantir_indices_operacionais,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    validar_config_mongo()
    await garantir_indice_persistencia()
    await garantir_collections()
    await garantir_indice_historico()
    await garantir_indices_operacionais()
    try:
        yield
    finally:
        await fechar_conexoes_postgres()

app = FastAPI(
    lifespan=lifespan,
    title="Segundo Inteligência Artificial",
    description="API da Plataforma de Manutenção FIXA com IA.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origem.strip() for origem in os.getenv("FIXA_WEB_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if origem.strip()],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    allow_credentials=False,
)

app.include_router(
    api_router,
    prefix="/api/v1",
)
