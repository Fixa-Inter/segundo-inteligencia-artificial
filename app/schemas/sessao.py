from pydantic import BaseModel


class EncerrarSessaoSaida(BaseModel):
    thread_id: str
    status: str
    mensagem: str
    resumo: str | None = None