from datetime import date

from pydantic import BaseModel, model_validator

from app.core.respostas import MENSAGENS


class PeriodoRequest(BaseModel):
    inicio: date
    fim: date

    @model_validator(mode="after")
    def validar_periodo(self):
        if self.inicio > self.fim:
            raise ValueError(
                MENSAGENS['a_data_inicial_nao_pode_ser_posterior_a_final']
            )

        return self


class ComparacaoPeriodosRequest(BaseModel):
    periodo_atual: PeriodoRequest
    periodo_anterior: PeriodoRequest