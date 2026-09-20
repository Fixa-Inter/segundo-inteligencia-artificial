from datetime import date

from pydantic import BaseModel, model_validator


class PeriodoRequest(BaseModel):
    inicio: date
    fim: date

    @model_validator(mode="after")
    def validar_periodo(self):
        if self.inicio > self.fim:
            raise ValueError("A data inicial não pode ser posterior à final.")
        return self