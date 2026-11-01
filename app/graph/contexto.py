from typing import Literal, NotRequired, TypedDict

from app.schemas import UsuarioContexto


class ContextoGrafo(TypedDict):
    usuario: UsuarioContexto
    imagens: list[str]
    session_id: str
    mensagem_atual: str
    turno_id: str
    contexto_temporal: str
    plataforma: NotRequired[Literal["web", "mobile"]]
    # Objeto do servidor, injetado somente na execução do especialista.
    captura_visualizacao: NotRequired[object]
    operacoes_pendentes: NotRequired[list[dict]]
    resultados_operacoes: NotRequired[list[dict]]
