import logging
from datetime import date, datetime, timedelta

from app.core import data_atual
from app.core.clients.postgres import executar_consulta
from app.schemas import UsuarioContexto
from app.services.ordensServico.buscarOrdensServico import inicio_periodo

from app.core.respostas import MENSAGENS
from app.graph.respostas_padrao import escolher_resposta


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
    raise ValueError(MENSAGENS['data_retornada_pelo_banco_em_formato_invalido'])


async def listar_solicitacoes_pendentes(usuario: UsuarioContexto) -> dict:
    """Lista ate cinco pendencias recentes da unidade nos ultimos tres meses."""
    hoje = data_atual()
    try:
        linhas = await executar_consulta(
            usuario.tipo_acesso,
            _SQL_BASE
            + " AND p.status = 0"
              " AND p.data_criacao >= :inicio AND p.data_criacao < :fim_exclusivo"
              " ORDER BY p.data_criacao DESC, p.id DESC LIMIT 5",
            {
                "usuario_id": usuario.usuario_id,
                "inicio": inicio_periodo(hoje),
                "fim_exclusivo": hoje + timedelta(days=1),
            },
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
            "mensagem": MENSAGENS['nao_foi_possivel_consultar_as_solicitacoes_no_banco'],
        }

    return {
        "status": "SUCESSO" if solicitacoes else "SEM_RESULTADO",
        "solicitacoes": solicitacoes,
        "orientacao": MENSAGENS['para_consultar_as_pendencias_acesse_a_tela_de_solicitacoes_abertas_no_app'],
        "mensagem": (
            escolher_resposta(solicitacoes, 'solicitacoes_pendentes_consultadas_com_sucesso', 'nenhuma_solicitacao_pendente_encontrada_no_endereco_do_gestor_nos_ultimos_tres_meses')
        ),
    }


async def listar_minhas_solicitacoes(usuario: UsuarioContexto) -> dict:
    """Lista as tres solicitacoes mais recentes do usuario nos ultimos tres meses."""
    hoje = data_atual()
    try:
        linhas = await executar_consulta(
            usuario.tipo_acesso,
            _SQL_BASE
            + " AND p.usuario_id = :usuario_id"
              " AND p.data_criacao >= :inicio AND p.data_criacao < :fim_exclusivo"
              " ORDER BY p.data_criacao DESC, p.id DESC LIMIT 3",
            {
                "usuario_id": usuario.usuario_id,
                "inicio": inicio_periodo(hoje),
                "fim_exclusivo": hoje + timedelta(days=1),
            },
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
            "mensagem": MENSAGENS['nao_foi_possivel_consultar_suas_solicitacoes_no_banco'],
        }

    return {
        "status": "SUCESSO" if solicitacoes else "SEM_RESULTADO",
        "solicitacoes": solicitacoes,
        "orientacao": MENSAGENS['para_consultar_suas_solicitacoes_acesse_a_area_minhas_solicitacoes_no_app'],
        "mensagem": (
            escolher_resposta(solicitacoes, 'solicitacoes_consultadas_com_sucesso', 'nenhuma_solicitacao_encontrada_para_o_usuario_neste_endereco_nos_ultimos_tres_meses')
        ),
    }
