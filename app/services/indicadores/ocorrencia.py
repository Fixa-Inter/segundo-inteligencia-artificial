"""Consultas de métricas de ocorrências na camada gold."""

import logging
from datetime import date
from typing import Any

from app.services.indicadores.gerais.databricks import (
    ConfiguracaoDatabricksAusente,
    ErroDatabricks,
    TimeoutConsultaDatabricks,
    executar_consulta,
)
from app.services.indicadores.gerais.unidade import validar_unidade_id


registrador = logging.getLogger(__name__)


def _validar_periodo(inicio: date, fim: date) -> dict | None:
    if type(inicio) is not date or type(fim) is not date:
        return {
            "status": "ERRO_VALIDACAO",
            "mensagem": "Informe início e fim do período como datas válidas.",
        }
    if inicio >= fim:
        return {
            "status": "ERRO_VALIDACAO",
            "mensagem": "O início deve ser anterior ao fim exclusivo do período.",
        }
    return None


def _periodo(inicio: date, fim: date) -> dict[str, str]:
    return {"inicio": inicio.isoformat(), "fim_exclusivo": fim.isoformat()}


async def _consultar(
    sql: str,
    parametros: dict[str, Any],
    *,
    retornar_linhas: bool = False,
    tipos_parametros: dict[str, str] | None = None,
) -> dict | list[dict]:
    try:
        linhas = await executar_consulta(
            sql,
            parametros,
            tipos_parametros=tipos_parametros or {"inicio": "DATE", "fim": "DATE", "unidade_id": "BIGINT"},
        )
    except TimeoutConsultaDatabricks:
        return {
            "status": "TIMEOUT",
            "mensagem": "A consulta de indicadores excedeu o tempo limite.",
        }
    except ConfiguracaoDatabricksAusente as erro:
        registrador.error("Configuração Databricks ausente: %s", erro)
        return {
            "status": "ERRO_FERRAMENTA",
            "mensagem": "A consulta de indicadores não está configurada.",
        }
    except ErroDatabricks:
        registrador.exception("Falha ao consultar indicador no Databricks")
        return {
            "status": "ERRO_FERRAMENTA",
            "mensagem": "Não foi possível consultar o indicador no Databricks.",
        }
    except Exception:
        registrador.exception("Falha inesperada ao consultar indicador no Databricks")
        return {
            "status": "ERRO_FERRAMENTA",
            "mensagem": "Não foi possível consultar o indicador no Databricks.",
        }

    if not linhas:
        return {
            "status": "SEM_RESULTADO",
            "mensagem": "A consulta não retornou resultados.",
        }
    return linhas if retornar_linhas else linhas[0]


async def obter_total_ocorrencias(inicio: date, fim: date, *, unidade_id: int) -> dict:
    """Soma ocorrências criadas no período [início, fim)."""
    erro_unidade = validar_unidade_id(unidade_id)
    if erro_unidade:
        return erro_unidade
    erro = _validar_periodo(inicio, fim)
    if erro:
        return erro
    linha = await _consultar(
        """
        SELECT COALESCE(SUM(qtd_ocorrencias), 0) AS total_ocorrencias
        FROM workspace.fixa_pipeline.gold_kpi_ocorrencias_diario
        WHERE unidade_id = :unidade_id
          AND data_referencia >= CAST(:inicio AS DATE)
          AND data_referencia < CAST(:fim AS DATE)
        """,
        {"inicio": inicio, "fim": fim, "unidade_id": unidade_id},
    )
    if isinstance(linha, dict) and linha.get("status"):
        return linha
    return {
        "status": "SUCESSO",
        "indicador": "Total de ocorrências",
        "resultado": linha,
        "periodo": _periodo(inicio, fim),
    }


async def _obter_por_dimensao(
    inicio: date,
    fim: date,
    *,
    unidade_id: int,
    dimensao: str,
    indicador: str,
) -> dict:
    erro_unidade = validar_unidade_id(unidade_id)
    if erro_unidade:
        return erro_unidade
    erro = _validar_periodo(inicio, fim)
    if erro:
        return erro
    linhas = await _consultar(
        f"""
        SELECT {dimensao}, SUM(qtd_ocorrencias) AS ocorrencias
        FROM workspace.fixa_pipeline.gold_kpi_ocorrencias_diario
        WHERE unidade_id = :unidade_id
          AND data_referencia >= CAST(:inicio AS DATE)
          AND data_referencia < CAST(:fim AS DATE)
        GROUP BY {dimensao}
        ORDER BY ocorrencias DESC, {dimensao}
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


async def obter_ocorrencias_por_tecnico(inicio: date, fim: date, *, unidade_id: int) -> dict:
    """Agrupa ocorrências criadas no período por técnico."""
    return await _obter_por_dimensao(
        inicio, fim, unidade_id=unidade_id, dimensao="tecnico_id", indicador="Ocorrências por técnico",
    )


async def obter_ocorrencias_por_unidade(inicio: date, fim: date, *, unidade_id: int) -> dict:
    """Retorna apenas a unidade autenticada para as ocorrências do período."""
    return await _obter_por_dimensao(
        inicio, fim, unidade_id=unidade_id, dimensao="unidade_id", indicador="Ocorrências por unidade",
    )


async def obter_ocorrencias_por_local(inicio: date, fim: date, *, unidade_id: int) -> dict:
    """Agrupa ocorrências criadas no período por local."""
    return await _obter_por_dimensao(
        inicio, fim, unidade_id=unidade_id, dimensao="local_id", indicador="Ocorrências por local",
    )


async def obter_ocorrencias_por_categoria_problema(
    inicio: date, fim: date,
    *, unidade_id: int,
) -> dict:
    """Agrupa ocorrências por categoria de problema, não de equipamento."""
    return await _obter_por_dimensao(
        inicio, fim, unidade_id=unidade_id,
        dimensao="categoria_problema_id",
        indicador="Ocorrências por categoria de problema",
    )


async def obter_ocorrencias_por_categoria_equipamento(
    inicio: date, fim: date,
    *, unidade_id: int,
) -> dict:
    """Agrupa ocorrências criadas no período por categoria de equipamento."""
    return await _obter_por_dimensao(
        inicio, fim, unidade_id=unidade_id,
        dimensao="categoria_equipamento_id",
        indicador="Ocorrências por categoria de equipamento",
    )


async def obter_ocorrencias_por_prioridade(inicio: date, fim: date, *, unidade_id: int) -> dict:
    """Agrupa ocorrências por código de prioridade: alta 0, média 1, baixa 2."""
    erro_unidade = validar_unidade_id(unidade_id)
    if erro_unidade:
        return erro_unidade
    erro = _validar_periodo(inicio, fim)
    if erro:
        return erro
    linhas = await _consultar(
        """
        SELECT prioridade, SUM(qtd_ocorrencias) AS ocorrencias
        FROM workspace.fixa_pipeline.gold_kpi_ocorrencias_diario
        WHERE unidade_id = :unidade_id
          AND data_referencia >= CAST(:inicio AS DATE)
          AND data_referencia < CAST(:fim AS DATE)
        GROUP BY prioridade
        ORDER BY prioridade
        """,
        {"inicio": inicio, "fim": fim, "unidade_id": unidade_id},
        retornar_linhas=True,
    )
    if isinstance(linhas, dict):
        return linhas
    return {
        "status": "SUCESSO",
        "indicador": "Ocorrências por prioridade",
        "resultados": linhas,
        "periodo": _periodo(inicio, fim),
    }


async def obter_ocorrencias_ativas(inicio: date, fim: date, *, unidade_id: int) -> dict:
    """Soma ocorrências do período aguardando revisão/aprovação do gestor."""
    erro_unidade = validar_unidade_id(unidade_id)
    if erro_unidade:
        return erro_unidade
    erro = _validar_periodo(inicio, fim)
    if erro:
        return erro
    linha = await _consultar(
        """
        SELECT COALESCE(SUM(qtd_ocorrencias_ativas), 0) AS ocorrencias_ativas
        FROM workspace.fixa_pipeline.gold_kpi_ocorrencias_diario
        WHERE unidade_id = :unidade_id
          AND data_referencia >= CAST(:inicio AS DATE)
          AND data_referencia < CAST(:fim AS DATE)
        """,
        {"inicio": inicio, "fim": fim, "unidade_id": unidade_id},
    )
    if isinstance(linha, dict) and linha.get("status"):
        return linha
    return {
        "status": "SUCESSO",
        "indicador": "Ocorrências aguardando revisão/aprovação do gestor",
        "resultado": linha,
        "periodo": _periodo(inicio, fim),
        "observacao": (
            "Ocorrências do período aguardando revisão/aprovação do gestor, "
            "conforme a última atualização disponível. Os status são atualizados "
            "sem repetir as pendências nos dias seguintes; o resultado não "
            "reconstitui a situação ao final de cada dia passado."
        ),
    }


async def obter_taxa_ocorrencias_alta_prioridade(inicio: date, fim: date, *, unidade_id: int) -> dict:
    """Calcula ocorrências de prioridade zero sobre o total da coorte."""
    erro_unidade = validar_unidade_id(unidade_id)
    if erro_unidade:
        return erro_unidade
    erro = _validar_periodo(inicio, fim)
    if erro:
        return erro
    linha = await _consultar(
        """
        SELECT COALESCE(SUM(CASE WHEN prioridade = 0
                                 THEN qtd_ocorrencias ELSE 0 END), 0) AS alta,
               COALESCE(SUM(qtd_ocorrencias), 0) AS total,
               100.0 * SUM(CASE WHEN prioridade = 0
                                THEN qtd_ocorrencias ELSE 0 END)
                   / NULLIF(SUM(qtd_ocorrencias), 0) AS taxa_pct
        FROM workspace.fixa_pipeline.gold_kpi_ocorrencias_diario
        WHERE unidade_id = :unidade_id
          AND data_referencia >= CAST(:inicio AS DATE)
          AND data_referencia < CAST(:fim AS DATE)
        """,
        {"inicio": inicio, "fim": fim, "unidade_id": unidade_id},
    )
    if isinstance(linha, dict) and linha.get("status"):
        return linha
    resposta = {
        "status": "SUCESSO",
        "indicador": "Taxa de alta prioridade das ocorrências",
        "resultado": linha,
        "periodo": _periodo(inicio, fim),
    }
    if linha.get("taxa_pct") is None:
        resposta["mensagem"] = "Sem base para cálculo no período informado."
    return resposta


async def obter_ocorrencias_por_periodo(
    inicio: date, fim: date, granularidade: str,
    *, unidade_id: int,
) -> dict:
    """Agrupa ocorrências criadas por dia, mês ou ano."""
    erro_unidade = validar_unidade_id(unidade_id)
    if erro_unidade:
        return erro_unidade
    erro = _validar_periodo(inicio, fim)
    if erro:
        return erro
    if granularidade not in {"dia", "mes", "ano"}:
        return {
            "status": "ERRO_VALIDACAO",
            "mensagem": "Granularidade inválida; use dia, mes ou ano.",
        }
    linhas = await _consultar(
        """
        SELECT CASE :granularidade
                 WHEN 'dia' THEN data_referencia
                 WHEN 'mes' THEN TRUNC(data_referencia, 'MM')
                 WHEN 'ano' THEN TRUNC(data_referencia, 'YYYY')
               END AS periodo,
               SUM(qtd_ocorrencias) AS ocorrencias
        FROM workspace.fixa_pipeline.gold_kpi_ocorrencias_diario
        WHERE unidade_id = :unidade_id
          AND data_referencia >= CAST(:inicio AS DATE)
          AND data_referencia < CAST(:fim AS DATE)
        GROUP BY 1
        ORDER BY 1
        """,
        {"inicio": inicio, "fim": fim, "granularidade": granularidade, "unidade_id": unidade_id},
        retornar_linhas=True,
        tipos_parametros={
            "inicio": "DATE", "fim": "DATE", "granularidade": "STRING",
            "unidade_id": "BIGINT",
        },
    )
    if isinstance(linhas, dict):
        return linhas
    return {
        "status": "SUCESSO",
        "indicador": "Ocorrências por período",
        "resultados": linhas,
        "periodo": _periodo(inicio, fim),
        "granularidade": granularidade,
    }
