import asyncio

from app.memory.embedding.popular_banco_vetorial import ingerir_faq

if __name__ == "__main__":
    asyncio.run(ingerir_faq())