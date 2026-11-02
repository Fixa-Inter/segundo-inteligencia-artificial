import logging

from app.core.clients.postgres import executar_insercao
from app.schemas import UsuarioContexto

from app.core.respostas import MENSAGENS


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
            "mensagem": MENSAGENS['o_comentario_e_sua_categoria_resumo_nao_podem_ficar_vazios'],
        }
    if len(comentario) > 255 or len(ideia_central) > 255:
        return {
            "status": "ERRO_VALIDACAO",
            "mensagem": MENSAGENS['o_comentario_e_o_resumo_devem_ter_no_maximo_255_caracteres'],
        }

    perfil = usuario.tipo_acesso.lower()
    if perfil not in _PERFIS_COM_ACESSO:
        return {
            "status": "ACESSO_NEGADO",
            "mensagem": MENSAGENS['este_perfil_nao_possui_uma_conexao_de_banco_autorizada_para_feedback'],
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
            raise RuntimeError(MENSAGENS['o_banco_nao_retornou_o_feedback_inserido'])

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
            "mensagem": MENSAGENS['feedback_registrado_com_sucesso'],
        }
    except Exception:
        registrador.exception("Falha ao registrar feedback no PostgreSQL")
        return {
            "status": "RESULTADO_INDETERMINADO",
            "mensagem": MENSAGENS['nao_foi_possivel_confirmar_o_resultado_do_feedback_confira_os_registros_antes'],
        }
