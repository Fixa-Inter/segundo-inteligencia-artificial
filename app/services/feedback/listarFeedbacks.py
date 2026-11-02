"""Consulta de feedbacks exclusivamente do usuário autenticado."""

from app.core.clients.postgres import executar_consulta
from app.core.respostas import MENSAGENS
from app.schemas import UsuarioContexto


async def listar_feedbacks(usuario: UsuarioContexto) -> dict:
    if usuario.tipo_acesso not in {"solicitante", "tecnico", "gestor", "administrador"}:
        raise PermissionError(MENSAGENS["contexto_de_autenticacao_invalido"])
    registros = await executar_consulta(usuario.tipo_acesso, """
        SELECT id, comentario, ideia_central, data_criacao
        FROM feedback WHERE usuario_id = :usuario_id
        ORDER BY data_criacao DESC, id DESC
    """, {"usuario_id": usuario.usuario_id})
    for registro in registros:
        if hasattr(registro.get("data_criacao"), "isoformat"):
            registro["data_criacao"] = registro["data_criacao"].isoformat()
    return {"status": "SUCESSO" if registros else "SEM_RESULTADO", "feedbacks": registros,
            "mensagem": MENSAGENS["feedbacks_listados" if registros else "feedbacks_ausentes"]}
