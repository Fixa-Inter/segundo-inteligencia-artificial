"""Dados do evento fornecidos pela IA; identidade e token vêm do backend."""

from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from app.core import FUSO_HORARIO, MENSAGENS, validar_titulo_cadastro

# CriarEventoEntrada: contrato/estrutura de CriarEventoEntrada; usado pelos consumidores desta interface.
class CriarEventoEntrada(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    local_unidade_id: int = Field(strict=True, gt=0, description="ID do local consultado no Qdrant.")
    titulo: str = Field(min_length=1, max_length=100, description="Resumo fiel em até 10 palavras.")
    descricao: str = Field(min_length=1, max_length=255)
    data_hora_inicio: datetime = Field(description="Data e hora de início. Sem fuso, usar America/Sao_Paulo.")
    data_hora_fim: datetime = Field(description="Data e hora de fim, estritamente posterior ao início.")
    descricao_local: str = Field(default="Não foi especificado", min_length=1, max_length=255)
    observacao: str = Field(default="Não foi especificado", min_length=1, max_length=255)

    @field_validator("titulo")
    @classmethod
    def limitar_palavras(cls, valor: str) -> str:
        """Confere o limite de dez palavras do título do evento. Usado pelo fluxo de cadastros."""
        return validar_titulo_cadastro(valor)

    @field_validator("data_hora_inicio", "data_hora_fim", mode="before")
    @classmethod
    def normalizar_horario(cls, valor) -> datetime:
        """Confere horario conforme o contrato deste domínio. Usado pelo fluxo de cadastros."""
        if isinstance(valor, str):
            valor = valor.strip()
            if "T" not in valor and " " not in valor:
                raise ValueError(MENSAGENS['informe_a_data_e_o_horario_completos_do_evento'])
            valor = datetime.fromisoformat(valor)
        if not isinstance(valor, datetime):
            raise ValueError(MENSAGENS['informe_a_data_e_o_horario_completos_do_evento'])
        if valor.tzinfo is None:
            valor = valor.replace(tzinfo=FUSO_HORARIO)
        return valor.astimezone(timezone.utc)

    @model_validator(mode="after")
    def validar_periodo(self):
        """Confere periodo conforme o contrato deste domínio. Usado pelo fluxo de cadastros."""
        if self.data_hora_fim <= self.data_hora_inicio:
            raise ValueError(MENSAGENS['o_fim_do_evento_deve_ser_estritamente_posterior_ao_inicio'])
        return self
