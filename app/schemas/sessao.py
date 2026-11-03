from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from app.core import Emocao, MENSAGENS
from app.schemas import LIMITE_ID_SESSAO, normalizar_id_sessao, VisualizacaoPublica

# EncerrarSessaoSaida: contrato/estrutura de sessao; usado pelos consumidores desta interface.
class EncerrarSessaoSaida(BaseModel):
    thread_id: str
    status: str
    mensagem: str
    titulo: str | None = None
    resumo: str | None = None


# ExcluirConversaSaida: contrato/estrutura de sessao; usado pelos consumidores desta interface.
class ExcluirConversaSaida(BaseModel):
    session_id: str
    status: Literal["EXCLUIDA"]
    mensagem: str


# ConversaEspecificaEntrada: contrato/estrutura de sessao; usado pelos consumidores desta interface.
class ConversaEspecificaEntrada(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str = Field(min_length=1, max_length=LIMITE_ID_SESSAO)

    @field_validator("session_id", mode="before")
    @classmethod
    def normalizar_session_id(cls, valor):
        """Confere session id conforme o contrato deste domínio. Usado pelo fluxo de schemas."""
        return normalizar_id_sessao(valor)


# MensagemHistorico: contrato/estrutura de sessao; usado pelos consumidores desta interface.
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
        """Confere timestamp conforme o contrato deste domínio. Usado pelo fluxo de schemas."""
        if valor is None:
            return None
        # O MongoDB retorna datas BSON como datetime sem tzinfo, em UTC.
        return valor.replace(tzinfo=timezone.utc) if valor.tzinfo is None else valor.astimezone(timezone.utc)

    @model_validator(mode="after")
    def validar_papel_visualizacao(self):
        """Confere papel visualizacao conforme o contrato deste domínio. Usado pelo fluxo de schemas."""
        if self.visualizacao is not None and self.role != "assistant":
            raise ValueError(MENSAGENS['somente_mensagens_do_assistente_possuem_visualizacao'])
        return self


# ConversaHistorico: contrato/estrutura de sessao; usado pelos consumidores desta interface.
class ConversaHistorico(BaseModel):
    session_id: str
    iniciada_em: datetime
    atualizada_em: datetime
    titulo: str
    resumo: str
    mensagens: list[MensagemHistorico]


# TodasConversasSaida: contrato/estrutura de sessao; usado pelos consumidores desta interface.
class TodasConversasSaida(BaseModel):
    status: Literal["SUCESSO", "SEM_DADOS"]
    mensagem: str
    conversas: list[ConversaHistorico]


# ConversaEspecificaSaida: contrato/estrutura de sessao; usado pelos consumidores desta interface.
class ConversaEspecificaSaida(BaseModel):
    status: Literal["SUCESSO"]
    mensagem: str
    conversa: ConversaHistorico
