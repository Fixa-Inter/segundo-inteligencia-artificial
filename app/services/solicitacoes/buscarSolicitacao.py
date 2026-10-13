import logging
from datetime import date, datetime

from app.core.clients.postgres import executar_select
from app.schemas.UsuarioContexto import UsuarioContexto


logger = logging.getLogger(__name__)

_SQL_BASE = """
    SELECT
        p.titulo,
        p.data_criacao::date AS "dataCriacao",
        solicitante.nome_completo AS usuario
    FROM problema AS p
    JOIN usuario AS solicitante ON solicitante.id = p.usuario_id
    JOIN local_endereco AS local_registro
        ON local_registro.id = p.local_endereco_id
    JOIN endereco AS endereco_registro
        ON endereco_registro.id = local_registro.endereco_id
    JOIN usuario AS usuario_autenticado ON usuario_autenticado.id = :usuario_id
    JOIN endereco AS endereco_autenticado
        ON endereco_autenticado.id = usuario_autenticado.endereco_id
    WHERE endereco_registro.cnpj = endereco_autenticado.cnpj
"""


def _data_iso(valor) -> str:
    if isinstance(valor, datetime):
        return valor.date().isoformat()
    if isinstance(valor, date):
        return valor.isoformat()
    raise ValueError("Data retornada pelo banco em formato invalido.")


async def listar_solicitacoes_pendentes(usuario: UsuarioContexto) -> dict:
    """Lista problemas pendentes no endereco do gestor autenticado."""
    try:
        rows = await executar_select(
            usuario.tipo_acesso,
            _SQL_BASE + " AND p.status = 0 ORDER BY p.data_criacao DESC",
            {"usuario_id": usuario.usuario_id},
        )
        solicitacoes = [
            {
                "titulo": row["titulo"],
                "dataCriacao": _data_iso(row["dataCriacao"]),
                "usuario": row["usuario"],
                "status": "PENDENTE",
            }
            for row in rows
        ]
    except Exception:
        logger.exception("Falha ao consultar solicitacoes pendentes no PostgreSQL")
        return {
            "status": "ERRO_FERRAMENTA",
            "mensagem": "Nao foi possivel consultar as solicitacoes no banco.",
        }

    return {
        "status": "SUCESSO" if solicitacoes else "SEM_RESULTADO",
        "solicitacoes": solicitacoes,
        "mensagem": (
            "Solicitacoes pendentes consultadas com sucesso."
            if solicitacoes
            else "Nenhuma solicitacao pendente encontrada no endereco do gestor."
        ),
    }


async def listar_minhas_solicitacoes(usuario: UsuarioContexto) -> dict:
    """Lista problemas do usuario autenticado dentro do endereco dele."""
    try:
        rows = await executar_select(
            usuario.tipo_acesso,
            _SQL_BASE
            + " AND p.usuario_id = :usuario_id ORDER BY p.data_criacao DESC",
            {"usuario_id": usuario.usuario_id},
        )
        solicitacoes = [
            {
                "titulo": row["titulo"],
                "dataCriacao": _data_iso(row["dataCriacao"]),
                "usuario": row["usuario"],
            }
            for row in rows
        ]
    except Exception:
        logger.exception("Falha ao consultar solicitacoes proprias no PostgreSQL")
        return {
            "status": "ERRO_FERRAMENTA",
            "mensagem": "Nao foi possivel consultar suas solicitacoes no banco.",
        }

    return {
        "status": "SUCESSO" if solicitacoes else "SEM_RESULTADO",
        "solicitacoes": solicitacoes,
        "mensagem": (
            "Solicitacoes consultadas com sucesso."
            if solicitacoes
            else "Nenhuma solicitacao encontrada para o usuario neste endereco."
        ),
    }
