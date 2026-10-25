from fastapi import HTTPException
from app.core import configuracao


def validar_chaves_ia() -> None:
    ausentes = [nome for nome, valor in {
        "OPENAI_API_KEY": configuracao.OPENAI_CHAVE_API,
        "TYPESAFE_API_KEY": configuracao.TYPESAFE_API_KEY,
        "GEMINI_API_KEY": configuracao.GEMINI_CHAVE_API,
    }.items() if not valor or not valor.strip()]
    if ausentes:
        raise HTTPException(503, "O serviço da Manu precisa configurar: " + ", ".join(ausentes) + ".")
