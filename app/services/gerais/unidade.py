"""Resolve a unidade do usuário autenticado a partir do banco FIXA."""

from app.core.clients.postgres import executar_consulta
from app.schemas import UsuarioContexto


async def obter_unidade_id(usuario: UsuarioContexto) -> int:
    if not isinstance(usuario, UsuarioContexto) or usuario.usuario_id <= 0:
        raise ValueError("Usuário autenticado inválido.")
    linhas = await executar_consulta(
        usuario.tipo_acesso,
        """
        SELECT unidade.id
        FROM usuario
        JOIN unidade ON unidade.id = usuario.unidade_id
        WHERE usuario.id = :usuario_id
          AND unidade.cnpj = :cnpj
          AND unidade.esta_ativo IS TRUE
          AND usuario.esta_ativo IS TRUE
        """,
        {"usuario_id": usuario.usuario_id, "cnpj": usuario.cnpj_endereco},
    )
    if len(linhas) != 1 or type(linhas[0]["id"]) is not int:
        raise PermissionError("Unidade autenticada não encontrada.")
    return linhas[0]["id"]
