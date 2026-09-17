import asyncio

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.memory.embedding.popular_banco_vetorial import ingerir_faq
from app.core.config import (
    FAQ_PDF_SOLICITANTE_PATH,
    FAQ_PDF_TECNICO_PATH,
    FAQ_PDF_GESTOR_PATH,
)


async def main():
    for perfil, caminho in (
        ("solicitante", FAQ_PDF_SOLICITANTE_PATH),
        ("tecnico", FAQ_PDF_TECNICO_PATH),
        ("gestor", FAQ_PDF_GESTOR_PATH),
    ):
        await ingerir_faq(caminho, perfil)


app = FastAPI(
    title="Segundo Inteligência Artificial",
    description="API da Plataforma de Manutenção FIXA com IA.",
    version="0.1.0",
)

app.include_router(
    health_router,
    prefix="/api/v1",
)


if __name__ == "__main__":
    asyncio.run(main())
