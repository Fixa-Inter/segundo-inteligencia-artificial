from typing import TypedDict

from app.schemas.UsuarioContexto import UsuarioContexto


class GraphContext(TypedDict):
    usuario: UsuarioContexto
    imagens: list[str]