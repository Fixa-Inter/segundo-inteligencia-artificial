import asyncio

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

if __name__ == "__main__":
    asyncio.run(main())
