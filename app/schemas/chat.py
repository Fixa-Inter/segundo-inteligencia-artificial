from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    mensagem: str = Field(
        min_length=1,
        max_length=4000,
    )

    thread_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    imagens: list[str] = Field(
        default_factory=list,
    )

    @field_validator("mensagem", "thread_id", mode="before")
    @classmethod
    def normalizar_texto(cls, valor):
        if isinstance(valor, str):
            return valor.strip()
        return valor


class ChatResponse(BaseModel):
    thread_id: str

    intencao: Literal[
        "faq",
        "solicitacao",
        "analytics",
        "visualizacao",
        "feedback",
        "fora_de_escopo",
    ] | None

    resposta: str
