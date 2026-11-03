from typing import Any
from pydantic import BaseModel

# ApiResponse: contrato/estrutura de common; usado pelos consumidores desta interface.
class ApiResponse(BaseModel):
    status: str
    mensagem: str
    dados: Any | None = None
