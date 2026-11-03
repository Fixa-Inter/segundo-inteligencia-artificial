"""Resolve a unidade do usuário autenticado a partir do banco FIXA."""

from app.core.clients import executar_consulta
from app.schemas import UsuarioContexto
from app.core import MENSAGENS

async def obter_unidade_id(usuario: UsuarioContexto) -> int:
    """Resolve e valida a unidade atual do usuário autenticado por consulta PostgreSQL. Usado pelo fluxo de gerais."""
    if not isinstance(usuario, UsuarioContexto) or usuario.usuario_id <= 0:
        raise ValueError(MENSAGENS['usuario_autenticado_invalido'])
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
        raise PermissionError(MENSAGENS['unidade_autenticada_nao_encontrada'])
    return linhas[0]["id"]
