from app.core import data_atual
import logging
from datetime import date, datetime, timedelta

from app.core.clients.postgres import executar_consulta
from app.schemas import UsuarioContexto
from app.services.ordensServico.buscarOrdensServico import (
    CATEGORIA_PROBLEMA_POR_ID,
    PRIORIDADE_POR_ID,
    inicio_periodo,
)

from app.core.respostas import MENSAGENS
from app.graph.respostas_padrao import escolher_resposta


registrador = logging.getLogger(__name__)


def _data_iso(valor) -> str:
    if isinstance(valor, datetime):
        return valor.date().isoformat()
    if isinstance(valor, date):
        return valor.isoformat()
    raise ValueError(MENSAGENS['data_retornada_pelo_banco_em_formato_invalido'])


async def buscar_equipamento_por_codigo(codigo: str, usuario: UsuarioContexto) -> dict:
    """Resolve codigo de equipamento ativo no endereco do usuario autenticado."""
    if not isinstance(codigo, str) or not codigo.strip():
        return {"status": "ERRO_VALIDACAO", "mensagem": MENSAGENS['informe_o_codigo_do_equipamento']}

    sql = """
        SELECT equipamento.id, equipamento.codigo,
               modelo.nome AS "nomeModelo",
               local_registro.nome AS "nomeLocalEndereco",
               equipamento.esta_ativo AS "estaAtivo"
        FROM equipamento
        JOIN modelo_equipamento AS modelo
            ON modelo.id = equipamento.modelo_equipamento_id
        JOIN local_unidade AS local_registro
            ON local_registro.id = equipamento.local_unidade_id
        JOIN unidade AS unidade_registro
            ON unidade_registro.id = local_registro.unidade_id
        JOIN usuario AS usuario_autenticado
            ON usuario_autenticado.id = :usuario_id
        JOIN unidade AS unidade_autenticada
            ON unidade_autenticada.id = usuario_autenticado.unidade_id
        WHERE equipamento.codigo = :codigo
          AND equipamento.esta_ativo IS TRUE
          AND local_registro.esta_ativo IS TRUE
          AND unidade_registro.esta_ativo IS TRUE
          AND usuario_autenticado.esta_ativo IS TRUE
          AND unidade_autenticada.esta_ativo IS TRUE
          AND unidade_registro.cnpj = unidade_autenticada.cnpj
        ORDER BY equipamento.id
        LIMIT 2
    """
    try:
        encontrados = await executar_consulta(
            usuario.tipo_acesso,
            sql,
            {"usuario_id": usuario.usuario_id, "codigo": codigo.strip()},
        )
    except Exception:
        registrador.exception("Falha ao consultar equipamento por codigo no PostgreSQL")
        return {
            "status": "ERRO_FERRAMENTA",
            "mensagem": MENSAGENS['nao_foi_possivel_consultar_o_equipamento_no_banco'],
        }

    if not encontrados:
        return {
            "status": "AGUARDANDO_INFORMACAO",
            "mensagem": MENSAGENS['equipamento_nao_encontrado_pelo_codigo_informado_peca_ao_usuario_para_conferir_o'],
        }
    if len(encontrados) != 1:
        return {
            "status": "AGUARDANDO_INFORMACAO",
            "mensagem": MENSAGENS['o_codigo_corresponde_a_mais_de_um_equipamento_neste_endereco_esclareca_o'],
        }
    return {"status": "SUCESSO", "equipamento": encontrados[0]}


async def consultar_minhas_ocorrencias(usuario: UsuarioContexto) -> dict:
    """Consulta ocorrencias do usuario no endereco dele nos ultimos tres meses."""
    hoje = data_atual()
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
        JOIN local_unidade AS local_registro
            ON local_registro.id = ocorrencia.local_unidade_id
        JOIN unidade AS unidade_registro
            ON unidade_registro.id = local_registro.unidade_id
        JOIN usuario AS usuario_autenticado
            ON usuario_autenticado.id = :usuario_id
        JOIN unidade AS unidade_autenticada
            ON unidade_autenticada.id = usuario_autenticado.unidade_id
        WHERE ocorrencia.usuario_id = :usuario_id
          AND ocorrencia.esta_ativo IS TRUE
          AND local_registro.esta_ativo IS TRUE
          AND unidade_registro.esta_ativo IS TRUE
          AND usuario_autenticado.esta_ativo IS TRUE
          AND unidade_autenticada.esta_ativo IS TRUE
          AND unidade_registro.cnpj = unidade_autenticada.cnpj
          AND ocorrencia.data_criacao >= :inicio
          AND ocorrencia.data_criacao < :fim_exclusivo
        ORDER BY ocorrencia.data_criacao DESC, ocorrencia.id DESC
        LIMIT 3
    """
    try:
        linhas = await executar_consulta(
            usuario.tipo_acesso,
            sql,
            {
                "usuario_id": usuario.usuario_id,
                "inicio": inicio,
                "fim_exclusivo": hoje + timedelta(days=1),
            },
        )
        ocorrencias = []
        for linha in linhas:
            categoria = CATEGORIA_PROBLEMA_POR_ID.get(linha["categoria_id"])
            prioridade = PRIORIDADE_POR_ID.get(linha["prioridade_id"])
            if categoria is None or prioridade is None:
                raise ValueError(MENSAGENS['categoria_ou_prioridade_de_ocorrencia_desconhecida'])
            ocorrencias.append({
                "titulo": linha["titulo"],
                "descricaoOcorrencia": linha["descricaoOcorrencia"],
                "categoriaProblema": categoria,
                "prioridade": prioridade,
                "localEndereco": linha["localEndereco"],
                "descricaoLocal": linha["descricaoLocal"],
                "dataCriacao": _data_iso(linha["dataCriacao"]),
                "equipamentoCodigo": linha["equipamentoCodigo"],
            })
    except Exception:
        registrador.exception("Falha ao consultar ocorrencias no PostgreSQL")
        return {
            "status": "ERRO_FERRAMENTA",
            "mensagem": MENSAGENS['nao_foi_possivel_consultar_as_ocorrencias_no_banco'],
        }

    return {
        "status": "SUCESSO" if ocorrencias else "SEM_RESULTADO",
        "ocorrencias": ocorrencias,
        "orientacao": MENSAGENS['para_consultar_suas_ocorrencias_acesse_a_area_minhas_ocorrencias_no_app'],
        "mensagem": (
            escolher_resposta(ocorrencias, 'ocorrencias_consultadas_com_sucesso', 'nenhuma_ocorrencia_encontrada_neste_endereco_nos_ultimos_tres_meses')
        ),
    }
