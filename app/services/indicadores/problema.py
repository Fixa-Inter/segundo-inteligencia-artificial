"""Consultas de métricas e KPIs de solicitações (problemas) na camada gold."""

import logging
from datetime import date, datetime, time
from typing import Any
from app.services.indicadores.gerais import (
    ConfiguracaoDatabricksAusente,
    ErroDatabricks,
    TimeoutConsultaDatabricks,
    executar_consulta,
    validar_unidade_id,
    consultar_linhas_indicador,
    validar_periodo_indicadores as _validar_periodo,
)
from app.core import MENSAGENS, formatar_periodo as _periodo

# registrador: Logger deste módulo; registra falhas sem publicar credenciais na resposta.
registrador = logging.getLogger(__name__)


async def _consultar(sql: str, parametros: dict[str, Any], *, tipos_parametros: dict[str, str] | None = None, retornar_linhas: bool = False) -> dict | list[dict]:
    """Adapta KPIs do domínio ao executor comum sem alterar tipos ou resultados."""
    linhas = await consultar_linhas_indicador(
        sql, parametros, executor=executar_consulta, registrador=registrador,
        tipos_parametros=tipos_parametros or {"inicio": "DATE", "fim": "DATE", "unidade_id": "BIGINT"},
    )
    if isinstance(linhas, dict):
        return linhas
    return linhas if retornar_linhas else linhas[0]


def _resposta(
    indicador: str,
    resultado: dict[str, Any],
    inicio: date,
    fim: date,
    *,
    campo_sem_base: str | None = None,
) -> dict:
    """Projeta rascunho e metadados para a resposta da ferramenta. Usado por _obter_soma, _obter_taxa."""
    resposta = {
        "status": "SUCESSO",
        "indicador": indicador,
        "resultado": resultado,
        "periodo": _periodo(inicio, fim),
    }
    if campo_sem_base and resultado.get(campo_sem_base) is None:
        resposta["mensagem"] = "Sem base para cálculo no período informado."
    return resposta


async def _obter_soma(
    inicio: date,
    fim: date,
    *,
    unidade_id: int,
    campo: str,
    alias: str,
    indicador: str,
) -> dict:
    """Executa a etapa obter soma no escopo de problema. Usado por obter_solicitacoes_aprovadas, obter_solicitacoes_pendentes, obter_solicitacoes_reprovadas."""
    erro_unidade = validar_unidade_id(unidade_id)
    if erro_unidade:
        return erro_unidade
    erro = _validar_periodo(inicio, fim)
    if erro:
        return erro
    linha = await _consultar(
        f"""
        SELECT COALESCE(SUM({campo}), 0) AS {alias}
        FROM workspace.fixa_pipeline.gold_kpi_solicitacoes_diario
        WHERE unidade_id = :unidade_id
          AND data_referencia >= CAST(:inicio AS DATE)
          AND data_referencia < CAST(:fim AS DATE)
        """,
        {"inicio": inicio, "fim": fim, "unidade_id": unidade_id},
    )
    if linha.get("status"):
        return linha
    return _resposta(indicador, linha, inicio, fim)


async def _obter_taxa(
    inicio: date,
    fim: date,
    *,
    unidade_id: int,
    numerador: str,
    alias_numerador: str,
    indicador: str,
) -> dict:
    """Executa a etapa obter taxa no escopo de problema. Usado por obter_taxa_aprovacao_solicitacoes, obter_taxa_conversao_solicitacoes_os, obter_taxa_reprovacao_solicitacoes."""
    erro_unidade = validar_unidade_id(unidade_id)
    if erro_unidade:
        return erro_unidade
    erro = _validar_periodo(inicio, fim)
    if erro:
        return erro
    linha = await _consultar(
        f"""
        SELECT COALESCE(SUM({numerador}), 0) AS {alias_numerador},
               COALESCE(SUM(qtd_solicitacoes), 0) AS total,
               100.0 * SUM({numerador})
                   / NULLIF(SUM(qtd_solicitacoes), 0) AS taxa_pct
        FROM workspace.fixa_pipeline.gold_kpi_solicitacoes_diario
        WHERE unidade_id = :unidade_id
          AND data_referencia >= CAST(:inicio AS DATE)
          AND data_referencia < CAST(:fim AS DATE)
        """,
        {"inicio": inicio, "fim": fim, "unidade_id": unidade_id},
    )
    if linha.get("status"):
        return linha
    return _resposta(
        indicador, linha, inicio, fim, campo_sem_base="taxa_pct",
    )


async def obter_total_solicitacoes(inicio: date, fim: date, *, unidade_id: int) -> dict:
    """Soma solicitações criadas no período inclusivo/exclusivo informado."""
    return await _obter_soma(
        inicio, fim, unidade_id=unidade_id,
        campo="qtd_solicitacoes",
        alias="total_solicitacoes",
        indicador="Total de solicitações",
    )


async def obter_solicitacoes_pendentes(inicio: date, fim: date, *, unidade_id: int) -> dict:
    """Soma pendências do período conforme a última atualização da unidade."""
    return await _obter_soma(
        inicio, fim, unidade_id=unidade_id,
        campo="qtd_solicitacoes_pendentes",
        alias="pendentes",
        indicador="Solicitações pendentes",
    )


async def obter_solicitacoes_aprovadas(inicio: date, fim: date, *, unidade_id: int) -> dict:
    """Soma aprovações do período conforme a última atualização da unidade."""
    return await _obter_soma(
        inicio, fim, unidade_id=unidade_id,
        campo="qtd_solicitacoes_aprovadas",
        alias="aprovadas",
        indicador="Solicitações aprovadas",
    )


async def obter_solicitacoes_reprovadas(inicio: date, fim: date, *, unidade_id: int) -> dict:
    """Soma reprovações do período conforme a última atualização da unidade."""
    return await _obter_soma(
        inicio, fim, unidade_id=unidade_id,
        campo="qtd_solicitacoes_reprovadas",
        alias="reprovadas",
        indicador="Solicitações reprovadas",
    )


async def obter_taxa_aprovacao_solicitacoes(inicio: date, fim: date, *, unidade_id: int) -> dict:
    """Calcula aprovações sobre todas as solicitações criadas na coorte."""
    return await _obter_taxa(
        inicio, fim, unidade_id=unidade_id,
        numerador="qtd_solicitacoes_aprovadas",
        alias_numerador="aprovadas",
        indicador="Taxa de aprovação de solicitações",
    )


async def obter_taxa_reprovacao_solicitacoes(inicio: date, fim: date, *, unidade_id: int) -> dict:
    """Calcula reprovações sobre todas as solicitações criadas na coorte."""
    return await _obter_taxa(
        inicio, fim, unidade_id=unidade_id,
        numerador="qtd_solicitacoes_reprovadas",
        alias_numerador="reprovadas",
        indicador="Taxa de reprovação de solicitações",
    )


async def obter_taxa_conversao_solicitacoes_os(inicio: date, fim: date, *, unidade_id: int) -> dict:
    """Calcula a parcela da coorte que gerou uma ou mais ordens de serviço."""
    return await _obter_taxa(
        inicio, fim, unidade_id=unidade_id,
        numerador="qtd_solicitacoes_com_os",
        alias_numerador="com_os",
        indicador="Taxa de conversão de solicitações em OS",
    )


async def _obter_por_dimensao(
    inicio: date,
    fim: date,
    *,
    unidade_id: int,
    dimensao: str,
    indicador: str,
) -> dict:
    """Executa a etapa obter por dimensao no escopo de problema. Usado por obter_solicitacoes_por_categoria_equipamento, obter_solicitacoes_por_local, obter_solicitacoes_por_unidade."""
    erro_unidade = validar_unidade_id(unidade_id)
    if erro_unidade:
        return erro_unidade
    erro = _validar_periodo(inicio, fim)
    if erro:
        return erro
    linhas = await _consultar(
        f"""
        SELECT {dimensao}, COALESCE(SUM(qtd_solicitacoes), 0) AS solicitacoes
        FROM workspace.fixa_pipeline.gold_kpi_solicitacoes_diario
        WHERE unidade_id = :unidade_id
          AND data_referencia >= CAST(:inicio AS DATE)
          AND data_referencia < CAST(:fim AS DATE)
        GROUP BY {dimensao}
        ORDER BY solicitacoes DESC, {dimensao}
        """,
        {"inicio": inicio, "fim": fim, "unidade_id": unidade_id},
        retornar_linhas=True,
    )
    if isinstance(linhas, dict):
        return linhas
    return {
        "status": "SUCESSO",
        "indicador": indicador,
        "resultados": linhas,
        "periodo": _periodo(inicio, fim),
    }


async def obter_solicitacoes_por_unidade(inicio: date, fim: date, *, unidade_id: int) -> dict:
    """Retorna apenas a unidade autenticada; a tabela não contém seu nome."""
    return await _obter_por_dimensao(
        inicio, fim, unidade_id=unidade_id, dimensao="unidade_id", indicador="Solicitações por unidade",
    )


async def obter_solicitacoes_por_local(inicio: date, fim: date, *, unidade_id: int) -> dict:
    """Agrupa a coorte por local; a gold não contém nome ou tipo do local."""
    return await _obter_por_dimensao(
        inicio, fim, unidade_id=unidade_id, dimensao="local_id", indicador="Solicitações por local",
    )


async def obter_solicitacoes_por_categoria_equipamento(
    inicio: date, fim: date,
    *, unidade_id: int,
) -> dict:
    """Agrupa a coorte por categoria de equipamento, não por problema."""
    return await _obter_por_dimensao(
        inicio, fim, unidade_id=unidade_id,
        dimensao="categoria_equipamento_id",
        indicador="Solicitações por categoria de equipamento",
    )


async def obter_solicitacoes_por_periodo(
    inicio: date, fim: date, granularidade: str,
    *, unidade_id: int,
) -> dict:
    """Agrupa a coorte por dia, mês ou ano conforme granularidade informada."""
    erro_unidade = validar_unidade_id(unidade_id)
    if erro_unidade:
        return erro_unidade
    erro = _validar_periodo(inicio, fim)
    if erro:
        return erro
    if granularidade not in {"dia", "mes", "ano"}:
        return {
            "status": "ERRO_VALIDACAO",
            "mensagem": MENSAGENS['granularidade_invalida_use_dia_mes_ou_ano'],
        }
    linhas = await _consultar(
        """
        SELECT CASE :granularidade
                 WHEN 'dia' THEN data_referencia
                 WHEN 'mes' THEN TRUNC(data_referencia, 'MM')
                 WHEN 'ano' THEN TRUNC(data_referencia, 'YYYY')
               END AS periodo,
               COALESCE(SUM(qtd_solicitacoes), 0) AS solicitacoes
        FROM workspace.fixa_pipeline.gold_kpi_solicitacoes_diario
        WHERE unidade_id = :unidade_id
          AND data_referencia >= CAST(:inicio AS DATE)
          AND data_referencia < CAST(:fim AS DATE)
        GROUP BY 1
        ORDER BY 1
        """,
        {"inicio": inicio, "fim": fim, "granularidade": granularidade, "unidade_id": unidade_id},
        tipos_parametros={
            "inicio": "DATE", "fim": "DATE", "granularidade": "STRING",
            "unidade_id": "BIGINT",
        },
        retornar_linhas=True,
    )
    if isinstance(linhas, dict):
        return linhas
    return {
        "status": "SUCESSO",
        "indicador": "Solicitações por período",
        "resultados": linhas,
        "periodo": _periodo(inicio, fim),
        "granularidade": granularidade,
    }


async def obter_taxa_recorrencia_local_categoria(
    inicio: date, fim: date,
    *, unidade_id: int,
) -> dict:
    """Calcula recorrência por local/categoria conforme episódios gold prontos."""
    erro_unidade = validar_unidade_id(unidade_id)
    if erro_unidade:
        return erro_unidade
    erro = _validar_periodo(inicio, fim)
    if erro:
        return erro
    inicio_timestamp = datetime.combine(inicio, time.min)
    fim_timestamp = datetime.combine(fim, time.min)
    linhas = await _consultar(
        """
        SELECT local_id, categoria_equipamento_id,
               COALESCE(SUM(qtd_solicitacoes), 0) AS solicitacoes_nos_episodios,
               COUNT(*) AS episodios,
               COUNT(*) FILTER (WHERE recorrente = TRUE) AS episodios_recorrentes,
               100.0 * COUNT(*) FILTER (WHERE recorrente = TRUE)
                   / NULLIF(COUNT(*), 0) AS taxa_pct
        FROM workspace.fixa_pipeline.gold_recorrencia_episodios
        WHERE unidade_id = :unidade_id
          AND inicio_episodio >= :inicio AND inicio_episodio < :fim
        GROUP BY local_id, categoria_equipamento_id
        ORDER BY episodios DESC, local_id, categoria_equipamento_id
        """,
        {"inicio": inicio_timestamp, "fim": fim_timestamp, "unidade_id": unidade_id},
        tipos_parametros={"inicio": "TIMESTAMP", "fim": "TIMESTAMP", "unidade_id": "BIGINT"},
        retornar_linhas=True,
    )
    if isinstance(linhas, dict):
        return linhas
    return {
        "status": "SUCESSO",
        "indicador": "Taxa de recorrência por local e categoria",
        "resultados": linhas,
        "periodo": _periodo(inicio, fim),
        "observacao": (
            "A taxa usa a classificação de recorrência calculada pelo BI para "
            "os episódios iniciados no período, na unidade consultada. "
            "Solicitações no episódio podem incluir registros após o fim do período."
        ),
    }
