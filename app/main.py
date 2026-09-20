from fastapi import FastAPI

from app.api.routes.health import router as health_router


app = FastAPI(
    title="Segundo Inteligência Artificial",
    description="API da Plataforma de Manutenção FIXA com IA.",
    version="0.1.0",
)

app.include_router(
    health_router,
    prefix="/api/v1",
)