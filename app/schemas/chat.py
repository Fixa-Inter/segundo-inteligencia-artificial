from typing import Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    mensagem: str = Field(
        min_length=1,
        max_length=4000,
    )

    thread_id: str = Field(
        min_length=1,
        max_length=100,
    )

    imagens: list[str] = Field(
        default_factory=list,
    )


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