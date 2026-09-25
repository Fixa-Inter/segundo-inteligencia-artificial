from pydantic import BaseModel


class EncerrarSessaoResponse(BaseModel):
    thread_id: str
    status: str
    mensagem: str
    resumo: str | None = None