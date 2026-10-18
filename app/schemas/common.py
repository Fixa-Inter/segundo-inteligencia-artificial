from typing import Any

from pydantic import BaseModel


class ApiResponse(BaseModel):
    status: str
    mensagem: str
    dados: Any | None = None