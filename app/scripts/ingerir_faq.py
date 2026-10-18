import asyncio

from app.memory.embedding.popular_banco_vetorial import ingerir_faq
from app.core.configuracao import (
    CAMINHO_PDF_FAQ_SOLICITANTE,
    CAMINHO_PDF_FAQ_TECNICO,
    CAMINHO_PDF_FAQ_GESTOR,
)

async def main():
    for perfil, caminho in (
        ("solicitante", CAMINHO_PDF_FAQ_SOLICITANTE),
        ("tecnico", CAMINHO_PDF_FAQ_TECNICO),
        ("gestor", CAMINHO_PDF_FAQ_GESTOR),
    ):
        await ingerir_faq(caminho, perfil)

if __name__ == "__main__":
    asyncio.run(main())