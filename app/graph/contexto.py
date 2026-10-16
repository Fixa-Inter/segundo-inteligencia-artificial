from typing import TypedDict

from app.schemas import UsuarioContexto


class ContextoGrafo(TypedDict):
    usuario: UsuarioContexto
    imagens: list[str]
    session_id: str
    mensagem_atual: str
    turno_id: str
    contexto_temporal: str
