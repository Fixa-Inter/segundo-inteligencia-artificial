from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core import Emocao
from app.schemas.id_sessao import LIMITE_ID_SESSAO, normalizar_id_sessao
from app.schemas.visualizacao import VisualizacaoPublica

from app.core.respostas import MENSAGENS


class EncerrarSessaoSaida(BaseModel):
    thread_id: str
    status: str
    mensagem: str
    titulo: str | None = None
    resumo: str | None = None


class ExcluirConversaSaida(BaseModel):
    session_id: str
    status: Literal["EXCLUIDA"]
    mensagem: str


class ConversaEspecificaEntrada(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str = Field(min_length=1, max_length=LIMITE_ID_SESSAO)

    @field_validator("session_id", mode="before")
    @classmethod
    def normalizar_session_id(cls, valor):
        return normalizar_id_sessao(valor)


class MensagemHistorico(BaseModel):
    role: Literal["human", "assistant"]
    mensagem: str
    timestamp: datetime | None = Field(
        default=None, description="Instante da persistência em UTC; null em mensagens antigas sem horário registrado.",
    )
    emocao: Emocao | None = Field(default=None, exclude_if=lambda v: v is None)
    confirmacao: Literal["sim", "nao"] = "nao"
    imagens: list[str] | None = Field(default=None, exclude_if=lambda v: v is None)
    visualizacao: VisualizacaoPublica | None = Field(default=None, exclude_if=lambda v: v is None)

    @field_validator("timestamp")
    @classmethod
    def normalizar_timestamp(cls, valor: datetime | None) -> datetime | None:
        if valor is None:
            return None
        # O MongoDB retorna datas BSON como datetime sem tzinfo, em UTC.
        return valor.replace(tzinfo=timezone.utc) if valor.tzinfo is None else valor.astimezone(timezone.utc)

    @model_validator(mode="after")
    def validar_papel_visualizacao(self):
        if self.visualizacao is not None and self.role != "assistant":
            raise ValueError(MENSAGENS['somente_mensagens_do_assistente_possuem_visualizacao'])
        return self


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
