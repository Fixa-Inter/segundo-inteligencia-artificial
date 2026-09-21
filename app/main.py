from fastapi import FastAPI

from app.api.router import api_router


app = FastAPI(
    title="Segundo Inteligência Artificial",
    description="API da Plataforma de Manutenção FIXA com IA.",
    version="0.1.0",
)

app.include_router(
    api_router,
    prefix="/api/v1",
)