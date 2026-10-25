from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core import Emocao


class EncerrarSessaoSaida(BaseModel):
    thread_id: str
    status: str
    mensagem: str
    resumo: str | None = None


class ConversaEspecificaEntrada(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str = Field(min_length=1, max_length=100)

    @field_validator("session_id", mode="before")
    @classmethod
    def normalizar_session_id(cls, valor):
        return valor.strip() if isinstance(valor, str) else valor


class MensagemHistorico(BaseModel):
    role: Literal["human", "assistant"]
    mensagem: str
    emocao: Emocao | None = None


class ConversaHistorico(BaseModel):
    session_id: str
    iniciada_em: datetime
    atualizada_em: datetime
    titulo: str
    resumo: str
    mensagens: list[MensagemHistorico]


class TodasConversasSaida(BaseModel):
    status: Literal["SUCESSO", "SEM_DADOS"]
    mensagem: str
    conversas: list[ConversaHistorico]


class ConversaEspecificaSaida(BaseModel):
    status: Literal["SUCESSO"]
    mensagem: str
    conversa: ConversaHistorico
