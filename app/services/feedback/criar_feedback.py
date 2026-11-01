import logging

from app.core.clients.postgres import executar_insercao
from app.schemas import UsuarioContexto


registrador = logging.getLogger(__name__)

_SQL_CRIAR_FEEDBACK = """
    INSERT INTO feedback (usuario_id, comentario, ideia_central)
    VALUES (:usuario_id, :comentario, :ideia_central)
    RETURNING id, data_criacao
"""
_PERFIS_COM_ACESSO = {"solicitante", "tecnico", "gestor", "administrador"}


async def criar_feedback(
    usuario: UsuarioContexto,
    comentario: str,
    ideia_central: str,
) -> dict:
    """Registra feedback e resumo categorizado para o usuario autenticado."""
    comentario = comentario.strip()
    ideia_central = ideia_central.strip()

    if not comentario or not ideia_central:
        return {
            "status": "ERRO_VALIDACAO",
            "mensagem": "O comentario e sua categoria/resumo nao podem ficar vazios.",
        }
    if len(comentario) > 255 or len(ideia_central) > 255:
        return {
            "status": "ERRO_VALIDACAO",
            "mensagem": "O comentario e o resumo devem ter no maximo 255 caracteres.",
        }

    perfil = usuario.tipo_acesso.lower()
    if perfil not in _PERFIS_COM_ACESSO:
        return {
            "status": "ACESSO_NEGADO",
            "mensagem": "Este perfil nao possui uma conexao de banco autorizada para feedback.",
        }

    try:
        linhas = await executar_insercao(
            perfil,
            _SQL_CRIAR_FEEDBACK,
            {
                "usuario_id": usuario.usuario_id,
                "comentario": comentario,
                "ideia_central": ideia_central,
            },
        )
        if not linhas:
            raise RuntimeError("O banco nao retornou o feedback inserido.")

        registro = linhas[0]
        data_criacao = registro["data_criacao"]
        return {
            "status": "SUCESSO",
            "feedback_id": registro["id"],
            "data_criacao": (
                data_criacao.isoformat()
                if hasattr(data_criacao, "isoformat")
                else data_criacao
            ),
            "mensagem": "Feedback registrado com sucesso.",
        }
    except Exception:
        registrador.exception("Falha ao registrar feedback no PostgreSQL")
        return {
            "status": "RESULTADO_INDETERMINADO",
            "mensagem": "Não foi possível confirmar o resultado do feedback. Confira os registros antes de repetir.",
        }
