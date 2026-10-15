import logging
from datetime import date, datetime, timedelta

from app.core.clients.postgres import executar_select
from app.schemas.UsuarioContexto import UsuarioContexto
from app.services.ordensServico.buscarOrdensServico import (
    CATEGORIA_PROBLEMA_POR_ID,
    PRIORIDADE_POR_ID,
    inicio_periodo,
)


logger = logging.getLogger(__name__)


def _data_iso(valor) -> str:
    if isinstance(valor, datetime):
        return valor.date().isoformat()
    if isinstance(valor, date):
        return valor.isoformat()
    raise ValueError("Data retornada pelo banco em formato invalido.")


async def buscar_equipamento_por_codigo(codigo: str, usuario: UsuarioContexto) -> dict:
    """Resolve codigo de equipamento ativo no endereco do usuario autenticado."""
    if not isinstance(codigo, str) or not codigo.strip():
        return {"status": "ERRO_VALIDACAO", "mensagem": "Informe o codigo do equipamento."}

    sql = """
        SELECT equipamento.id, equipamento.codigo,
               modelo.nome AS "nomeModelo",
               local_registro.nome AS "nomeLocalEndereco",
               equipamento.esta_ativo AS "estaAtivo"
        FROM equipamento
        JOIN modelo_equipamento AS modelo
            ON modelo.id = equipamento.modelo_equipamento_id
        JOIN local_endereco AS local_registro
            ON local_registro.id = equipamento.local_endereco_id
        JOIN unidade AS unidade_registro
            ON unidade_registro.id = local_registro.unidade_id
        JOIN usuario AS usuario_autenticado
            ON usuario_autenticado.id = :usuario_id
        JOIN unidade AS unidade_autenticada
            ON unidade_autenticada.id = usuario_autenticado.unidade_id
        WHERE equipamento.codigo = :codigo
          AND equipamento.esta_ativo IS TRUE
          AND unidade_registro.cnpj = unidade_autenticada.cnpj
        ORDER BY equipamento.id
        LIMIT 2
    """
    try:
        encontrados = await executar_select(
            usuario.tipo_acesso,
            sql,
            {"usuario_id": usuario.usuario_id, "codigo": codigo.strip()},
        )
    except Exception:
        logger.exception("Falha ao consultar equipamento por codigo no PostgreSQL")
        return {
            "status": "ERRO_FERRAMENTA",
            "mensagem": "Nao foi possivel consultar o equipamento no banco.",
        }

    if not encontrados:
        return {
            "status": "AGUARDANDO_INFORMACAO",
            "mensagem": "Equipamento nao encontrado pelo codigo informado. Peça ao usuario para conferir o codigo.",
        }
    if len(encontrados) != 1:
        return {
            "status": "AGUARDANDO_INFORMACAO",
            "mensagem": "O codigo corresponde a mais de um equipamento neste endereco. Esclareca o cadastro antes de continuar.",
        }
    return {"status": "SUCESSO", "equipamento": encontrados[0]}


async def consultar_minhas_ocorrencias(usuario: UsuarioContexto) -> dict:
    """Consulta ocorrencias do usuario no endereco dele nos ultimos tres meses."""
    hoje = date.today()
    inicio = inicio_periodo(hoje)
    sql = """
        SELECT ocorrencia.titulo,
               ocorrencia.descricao_ocorrencia AS "descricaoOcorrencia",
               ocorrencia.categoria_problema AS categoria_id,
               ocorrencia.prioridade AS prioridade_id,
               local_registro.nome AS "localEndereco",
               ocorrencia.descricao_local AS "descricaoLocal",
               ocorrencia.data_criacao::date AS "dataCriacao",
               NULL::varchar AS "equipamentoCodigo"
        FROM ocorrencia
        JOIN local_endereco AS local_registro
            ON local_registro.id = ocorrencia.local_endereco_id
        JOIN unidade AS unidade_registro
            ON unidade_registro.id = local_registro.unidade_id
        JOIN usuario AS usuario_autenticado
            ON usuario_autenticado.id = :usuario_id
        JOIN unidade AS unidade_autenticada
            ON unidade_autenticada.id = usuario_autenticado.unidade_id
        WHERE ocorrencia.usuario_id = :usuario_id
          AND ocorrencia.esta_ativo IS TRUE
          AND unidade_registro.cnpj = unidade_autenticada.cnpj
          AND ocorrencia.data_criacao >= :inicio
          AND ocorrencia.data_criacao < :fim_exclusivo
        ORDER BY ocorrencia.data_criacao DESC
    """
    try:
        rows = await executar_select(
            usuario.tipo_acesso,
            sql,
            {
                "usuario_id": usuario.usuario_id,
                "inicio": inicio,
                "fim_exclusivo": hoje + timedelta(days=1),
            },
        )
        ocorrencias = []
        for row in rows:
            categoria = CATEGORIA_PROBLEMA_POR_ID.get(row["categoria_id"])
            prioridade = PRIORIDADE_POR_ID.get(row["prioridade_id"])
            if categoria is None or prioridade is None:
                raise ValueError("Categoria ou prioridade de ocorrencia desconhecida.")
            ocorrencias.append({
                "titulo": row["titulo"],
                "descricaoOcorrencia": row["descricaoOcorrencia"],
                "categoriaProblema": categoria,
                "prioridade": prioridade,
                "localEndereco": row["localEndereco"],
                "descricaoLocal": row["descricaoLocal"],
                "dataCriacao": _data_iso(row["dataCriacao"]),
                "equipamentoCodigo": row["equipamentoCodigo"],
            })
    except Exception:
        logger.exception("Falha ao consultar ocorrencias no PostgreSQL")
        return {
            "status": "ERRO_FERRAMENTA",
            "mensagem": "Nao foi possivel consultar as ocorrencias no banco.",
        }

    return {
        "status": "SUCESSO" if ocorrencias else "SEM_RESULTADO",
        "ocorrencias": ocorrencias,
        "mensagem": (
            "Ocorrencias consultadas com sucesso."
            if ocorrencias
            else "Nenhuma ocorrencia encontrada neste endereco nos ultimos tres meses."
        ),
    }
