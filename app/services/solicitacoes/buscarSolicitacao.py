import logging
from datetime import date, datetime

from app.core.clients.postgres import executar_consulta
from app.schemas import UsuarioContexto


registrador = logging.getLogger(__name__)

_SQL_BASE = """
    SELECT
        p.titulo,
        p.data_criacao::date AS "dataCriacao",
        solicitante.nome_completo AS usuario
    FROM problema AS p
    JOIN usuario AS solicitante ON solicitante.id = p.usuario_id
    JOIN local_unidade AS local_registro
        ON local_registro.id = p.local_unidade_id
    JOIN unidade AS unidade_registro
        ON unidade_registro.id = local_registro.unidade_id
    JOIN usuario AS usuario_autenticado ON usuario_autenticado.id = :usuario_id
    JOIN unidade AS unidade_autenticada
        ON unidade_autenticada.id = usuario_autenticado.unidade_id
    WHERE unidade_registro.cnpj = unidade_autenticada.cnpj
      AND p.esta_ativo IS TRUE
      AND local_registro.esta_ativo IS TRUE
      AND unidade_registro.esta_ativo IS TRUE
      AND usuario_autenticado.esta_ativo IS TRUE
      AND unidade_autenticada.esta_ativo IS TRUE
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
        linhas = await executar_consulta(
            usuario.tipo_acesso,
            _SQL_BASE + " AND p.status = 0 ORDER BY p.data_criacao DESC",
            {"usuario_id": usuario.usuario_id},
        )
        solicitacoes = [
            {
                "titulo": linha["titulo"],
                "dataCriacao": _data_iso(linha["dataCriacao"]),
                "usuario": linha["usuario"],
                "status": "PENDENTE",
            }
            for linha in linhas
        ]
    except Exception:
        registrador.exception("Falha ao consultar solicitacoes pendentes no PostgreSQL")
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
        linhas = await executar_consulta(
            usuario.tipo_acesso,
            _SQL_BASE
            + " AND p.usuario_id = :usuario_id ORDER BY p.data_criacao DESC",
            {"usuario_id": usuario.usuario_id},
        )
        solicitacoes = [
            {
                "titulo": linha["titulo"],
                "dataCriacao": _data_iso(linha["dataCriacao"]),
                "usuario": linha["usuario"],
            }
            for linha in linhas
        ]
    except Exception:
        registrador.exception("Falha ao consultar solicitacoes proprias no PostgreSQL")
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
