from pydantic import BaseModel

# HealthResponse: contrato/estrutura de health; usado pelos consumidores desta interface.
class HealthResponse(BaseModel):
    status: str
    service: str
