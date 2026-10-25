"""Consultas de métricas e KPIs de ordens de serviço na camada gold."""

import logging
from datetime import date, datetime, time
from typing import Any

from app.services.indicadores.gerais.databricks import (
    ConfiguracaoDatabricksAusente,
    ErroDatabricks,
    TimeoutConsultaDatabricks,
    executar_consulta,
)


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


def _parametros_periodo(inicio: date, fim: date) -> dict[str, date]:
    return {"inicio": inicio, "fim": fim}


def _resposta(
    indicador: str,
    resultado: dict[str, Any] | list[dict[str, Any]],
    *,
    periodo: dict[str, str] | None = None,
    campo_sem_base: str | None = None,
) -> dict:
    resposta = {"status": "SUCESSO", "indicador": indicador}
    chave_resultado = "resultados" if isinstance(resultado, list) else "resultado"
    resposta[chave_resultado] = resultado
    if periodo is not None:
        resposta["periodo"] = periodo
    if (
        campo_sem_base
        and isinstance(resultado, dict)
        and resultado.get(campo_sem_base) is None
    ):
        resposta["mensagem"] = "Sem base para cálculo no período informado."
    return resposta


def _periodo_legivel(inicio: date, fim: date) -> dict[str, str]:
    return {
        "inicio": inicio.isoformat(),
        "fim_exclusivo": fim.isoformat(),
    }


async def _consultar_linhas(
    sql: str,
    parametros: dict[str, Any] | None = None,
    *,
    tipos_parametros: dict[str, str] | None = None,
) -> list[dict[str, Any]] | dict[str, str]:
    try:
        linhas = await executar_consulta(
            sql,
            parametros or {},
            tipos_parametros=tipos_parametros,
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
    return linhas


async def _consultar(
    sql: str,
    parametros: dict[str, Any] | None = None,
    *,
    tipos_parametros: dict[str, str] | None = None,
) -> dict[str, Any]:
    linhas = await _consultar_linhas(
        sql, parametros, tipos_parametros=tipos_parametros,
    )
    if isinstance(linhas, dict):
        return linhas
    return linhas[0]


async def obter_total_os(inicio: date, fim: date) -> dict:
    """Conta OS criadas no período `[início, fim)`."""
    erro = _validar_periodo(inicio, fim)
    if erro:
        return erro

    linha = await _consultar(
        """
        SELECT COALESCE(SUM(qtd_os_criadas), 0) AS total_os
        FROM workspace.gold.kpi_os_criacao_diario
        WHERE data_referencia >= CAST(:inicio AS DATE)
          AND data_referencia < CAST(:fim AS DATE)
        """,
        _parametros_periodo(inicio, fim),
        tipos_parametros={"inicio": "DATE", "fim": "DATE"},
    )
    if linha.get("status"):
        return linha
    return _resposta(
        "Total de OS", linha, periodo=_periodo_legivel(inicio, fim),
    )


async def obter_os_abertas() -> dict:
    """Conta OS atualmente abertas (status 1, 2 ou 3), sem filtro de criação."""
    linha = await _consultar(
        """
        SELECT COALESCE(SUM(qtd_os), 0) AS os_abertas
        FROM workspace.gold.os_por_status
        WHERE status_id IN (1, 2, 3)
        """,
    )
    if linha.get("status"):
        return linha
    return _resposta("OS abertas", linha)


async def obter_os_atrasadas() -> dict:
    """Conta OS atualmente classificadas como Atrasada (status 1)."""
    linha = await _consultar(
        """
        SELECT COALESCE(SUM(qtd_os), 0) AS os_atrasadas
        FROM workspace.gold.os_por_status
        WHERE status_id = 1
        """,
    )
    if linha.get("status"):
        return linha
    return _resposta("OS atrasadas", linha)


async def obter_taxa_atraso_os() -> dict:
    """Calcula a parcela de OS atrasadas entre as OS abertas no snapshot atual."""
    linha = await _consultar(
        """
        SELECT
            COALESCE(SUM(CASE WHEN status_id = 1 THEN qtd_os ELSE 0 END), 0)
                AS atrasadas,
            COALESCE(SUM(CASE WHEN status_id IN (1, 2, 3) THEN qtd_os ELSE 0 END), 0)
                AS abertas,
            100.0 * SUM(CASE WHEN status_id = 1 THEN qtd_os ELSE 0 END)
                / NULLIF(SUM(CASE WHEN status_id IN (1, 2, 3) THEN qtd_os ELSE 0 END), 0)
                AS taxa_pct
        FROM workspace.gold.os_por_status
        """,
    )
    if linha.get("status"):
        return linha
    return _resposta("Taxa de atraso de OS", linha, campo_sem_base="taxa_pct")


async def obter_os_finalizadas(inicio: date, fim: date) -> dict:
    """Conta OS atualmente finalizadas, por data de conclusão em `[início, fim)`."""
    erro = _validar_periodo(inicio, fim)
    if erro:
        return erro

    linha = await _consultar(
        """
        SELECT COALESCE(SUM(qtd_os_finalizadas), 0) AS os_finalizadas
        FROM workspace.gold.kpi_os_conclusao_diario
        WHERE data_referencia >= CAST(:inicio AS DATE)
          AND data_referencia < CAST(:fim AS DATE)
        """,
        _parametros_periodo(inicio, fim),
        tipos_parametros={"inicio": "DATE", "fim": "DATE"},
    )
    if linha.get("status"):
        return linha
    return _resposta(
        "OS finalizadas", linha, periodo=_periodo_legivel(inicio, fim),
    )


async def obter_taxa_conclusao_prazo(inicio: date, fim: date) -> dict:
    """Calcula a conclusão no prazo entre OS finalizadas elegíveis no período."""
    erro = _validar_periodo(inicio, fim)
    if erro:
        return erro

    linha = await _consultar(
        """
        SELECT
            COALESCE(SUM(qtd_os_finalizadas), 0) AS finalizadas,
            COALESCE(SUM(qtd_os_com_prazo_valido), 0) AS elegiveis,
            COALESCE(SUM(qtd_os_concluidas_no_prazo), 0) AS no_prazo,
            100.0 * SUM(qtd_os_concluidas_no_prazo)
                / NULLIF(SUM(qtd_os_com_prazo_valido), 0) AS taxa_pct
        FROM workspace.gold.kpi_os_conclusao_diario
        WHERE data_referencia >= CAST(:inicio AS DATE)
          AND data_referencia < CAST(:fim AS DATE)
        """,
        _parametros_periodo(inicio, fim),
        tipos_parametros={"inicio": "DATE", "fim": "DATE"},
    )
    if linha.get("status"):
        return linha
    return _resposta(
        "Taxa de conclusão no prazo",
        linha,
        periodo=_periodo_legivel(inicio, fim),
        campo_sem_base="taxa_pct",
    )


async def obter_tempo_medio_espera_os(inicio: date, fim: date) -> dict:
    """Calcula a espera válida até o início das OS criadas no período."""
    erro = _validar_periodo(inicio, fim)
    if erro:
        return erro

    inicio_timestamp = datetime.combine(inicio, time.min)
    fim_timestamp = datetime.combine(fim, time.min)
    linha = await _consultar(
        """
        SELECT COUNT(*) AS os_com_espera_valida,
               AVG(tempo_espera_minutos) AS media_minutos
        FROM workspace.gold.os_tempos
        WHERE data_criacao >= :inicio AND data_criacao < :fim
          AND data_inicio >= data_criacao
          AND tempo_espera_minutos IS NOT NULL AND tempo_espera_minutos >= 0
        """,
        {"inicio": inicio_timestamp, "fim": fim_timestamp},
        tipos_parametros={"inicio": "TIMESTAMP", "fim": "TIMESTAMP"},
    )
    if linha.get("status"):
        return linha
    return _resposta(
        "Tempo médio de espera de OS",
        linha,
        periodo=_periodo_legivel(inicio, fim),
        campo_sem_base="media_minutos",
    )
async def obter_tempo_medio_resolucao_os(inicio: date, fim: date) -> dict:
    """Calcula a resolucao valida das OS concluidas no periodo."""
    erro = _validar_periodo(inicio, fim)
    if erro:
        return erro
    inicio_ts = datetime.combine(inicio, time.min)
    fim_ts = datetime.combine(fim, time.min)
    linha = await _consultar(
        """
        SELECT COUNT(*) AS os_com_resolucao_valida,
               AVG(tempo_resolucao_minutos) AS media_minutos
        FROM workspace.gold.os_tempos
        WHERE data_conclusao >= :inicio AND data_conclusao < :fim
          AND status_id = 4
          AND data_inicio >= data_criacao AND data_conclusao >= data_inicio
          AND tempo_resolucao_minutos IS NOT NULL AND tempo_resolucao_minutos >= 0
        """,
        {"inicio": inicio_ts, "fim": fim_ts},
        tipos_parametros={"inicio": "TIMESTAMP", "fim": "TIMESTAMP"},
    )
    if linha.get("status"):
        return linha
    return _resposta("Tempo medio de resolucao de OS", linha,
        periodo=_periodo_legivel(inicio, fim), campo_sem_base="media_minutos")


async def obter_tempo_medio_pausado_os(inicio: date, fim: date) -> dict:
    """Calcula tempo pausado valido nas OS criadas no periodo, incluindo zero."""
    erro = _validar_periodo(inicio, fim)
    if erro:
        return erro
    inicio_ts = datetime.combine(inicio, time.min)
    fim_ts = datetime.combine(fim, time.min)
    linha = await _consultar(
        """
        SELECT COUNT(*) AS os_com_tempo_pausado_valido,
               AVG(tempo_pausado_minutos) AS media_minutos
        FROM workspace.gold.os_tempos
        WHERE data_criacao >= :inicio AND data_criacao < :fim
          AND tempo_pausado_minutos IS NOT NULL AND tempo_pausado_minutos >= 0
        """,
        {"inicio": inicio_ts, "fim": fim_ts},
        tipos_parametros={"inicio": "TIMESTAMP", "fim": "TIMESTAMP"},
    )
    if linha.get("status"):
        return linha
    return _resposta("Tempo medio pausado de OS", linha,
        periodo=_periodo_legivel(inicio, fim), campo_sem_base="media_minutos")


async def _obter_taxa_coorte(inicio: date, fim: date, campo: str, indicador: str) -> dict:
    erro = _validar_periodo(inicio, fim)
    if erro:
        return erro
    linha = await _consultar(
        f"""
        SELECT COALESCE(SUM({campo}), 0) AS numerador,
               COALESCE(SUM(qtd_os_criadas), 0) AS os_criadas,
               100.0 * SUM({campo}) / NULLIF(SUM(qtd_os_criadas), 0) AS taxa_pct
        FROM workspace.gold.kpi_os_criacao_diario
        WHERE data_referencia >= CAST(:inicio AS DATE)
          AND data_referencia < CAST(:fim AS DATE)
        """,
        _parametros_periodo(inicio, fim),
        tipos_parametros={"inicio": "DATE", "fim": "DATE"},
    )
    if linha.get("status"):
        return linha
    return _resposta(indicador, linha, periodo=_periodo_legivel(inicio, fim),
        campo_sem_base="taxa_pct")


async def obter_taxa_reabertura_os(inicio: date, fim: date) -> dict:
    return await _obter_taxa_coorte(inicio, fim, "qtd_os_reabertas", "Taxa de reabertura de OS")


async def obter_taxa_reatribuicao_os(inicio: date, fim: date) -> dict:
    return await _obter_taxa_coorte(inicio, fim, "qtd_os_reatribuidas", "Taxa de reatribuicao de OS")


async def obter_carga_ativa_tecnicos() -> dict:
    linhas = await _consultar_linhas(
        """
        SELECT tecnico_id, tecnico_nome,
               COALESCE(SUM(qtd_os_ativas), 0) AS os_abertas
        FROM workspace.gold.kpi_carga_ativa_tecnico
        GROUP BY tecnico_id, tecnico_nome
        ORDER BY os_abertas DESC, tecnico_id
        """,
    )
    if isinstance(linhas, dict):
        return linhas
    return _resposta("Carga ativa por tecnico", linhas)


async def obter_produtividade_tecnicos(inicio: date, fim: date) -> dict:
    erro = _validar_periodo(inicio, fim)
    if erro:
        return erro
    linhas = await _consultar_linhas(
        """
        SELECT tecnico_id, tecnico_nome,
               COALESCE(SUM(qtd_os_finalizadas), 0) AS os_finalizadas
        FROM workspace.gold.kpi_produtividade_tecnico
        WHERE data_referencia >= CAST(:inicio AS DATE)
          AND data_referencia < CAST(:fim AS DATE)
        GROUP BY tecnico_id, tecnico_nome
        ORDER BY os_finalizadas DESC, tecnico_id
        """,
        _parametros_periodo(inicio, fim),
        tipos_parametros={"inicio": "DATE", "fim": "DATE"},
    )
    if isinstance(linhas, dict):
        return linhas
    return _resposta("Produtividade por tecnico", linhas,
        periodo=_periodo_legivel(inicio, fim))


async def obter_media_tarefas_por_os(inicio: date, fim: date) -> dict:
    erro = _validar_periodo(inicio, fim)
    if erro:
        return erro
    linha = await _consultar(
        """
        SELECT SUM(qtd_os_criadas) AS os_criadas,
               CASE
                 WHEN SUM(CASE WHEN qtd_os_criadas > 0
                                AND media_tarefas_por_os IS NULL THEN 1 ELSE 0 END) > 0
                   THEN NULL
                 ELSE SUM(media_tarefas_por_os * qtd_os_criadas)
                      / NULLIF(SUM(qtd_os_criadas), 0)
               END AS media_tarefas_por_os
        FROM workspace.gold.kpi_os_criacao_diario
        WHERE data_referencia >= CAST(:inicio AS DATE)
          AND data_referencia < CAST(:fim AS DATE)
        """,
        _parametros_periodo(inicio, fim),
        tipos_parametros={"inicio": "DATE", "fim": "DATE"},
    )
    if linha.get("status"):
        return linha
    resposta = _resposta("Media de tarefas por OS", linha,
        periodo=_periodo_legivel(inicio, fim), campo_sem_base="media_tarefas_por_os")
    resposta["observacao"] = (
        "Exata somente se a media diaria incluir OS com zero tarefas."
    )
    return resposta
