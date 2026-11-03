from datetime import date
from pydantic import BaseModel, model_validator
from app.core import MENSAGENS

# PeriodoRequest: contrato/estrutura de analytics; usado pelos consumidores desta interface.
class PeriodoRequest(BaseModel):
    inicio: date
    fim: date

    @model_validator(mode="after")
    def validar_periodo(self):
        """Confere periodo conforme o contrato deste domínio. Usado pelo fluxo de schemas."""
        if self.inicio > self.fim:
            raise ValueError(
                MENSAGENS['a_data_inicial_nao_pode_ser_posterior_a_final']
            )

        return self


# ComparacaoPeriodosRequest: contrato/estrutura de analytics; usado pelos consumidores desta interface.
class ComparacaoPeriodosRequest(BaseModel):
    periodo_atual: PeriodoRequest
    periodo_anterior: PeriodoRequest
