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
from app.services.indicadores.gerais.unidade import validar_unidade_id

from app.core.respostas import MENSAGENS


registrador = logging.getLogger(__name__)


def _validar_periodo(inicio: date, fim: date) -> dict | None:
    if type(inicio) is not date or type(fim) is not date:
        return {
            "status": "ERRO_VALIDACAO",
            "mensagem": MENSAGENS['informe_inicio_e_fim_do_periodo_como_datas_validas'],
        }
    if inicio >= fim:
        return {
            "status": "ERRO_VALIDACAO",
            "mensagem": MENSAGENS['o_inicio_deve_ser_anterior_ao_fim_exclusivo_do_periodo'],
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
            "mensagem": MENSAGENS['a_consulta_de_indicadores_excedeu_o_tempo_limite'],
        }
    except ConfiguracaoDatabricksAusente as erro:
        registrador.error("Configuração Databricks ausente: %s", erro)
        return {
            "status": "ERRO_FERRAMENTA",
            "mensagem": MENSAGENS['a_consulta_de_indicadores_nao_esta_configurada'],
        }
    except ErroDatabricks:
        registrador.exception("Falha ao consultar indicador no Databricks")
        return {
            "status": "ERRO_FERRAMENTA",
            "mensagem": MENSAGENS['nao_foi_possivel_consultar_o_indicador_no_databricks'],
        }
    except Exception:
        registrador.exception("Falha inesperada ao consultar indicador no Databricks")
        return {
            "status": "ERRO_FERRAMENTA",
            "mensagem": MENSAGENS['nao_foi_possivel_consultar_o_indicador_no_databricks'],
        }

    if not linhas:
        return {
            "status": "SEM_RESULTADO",
            "mensagem": MENSAGENS['a_consulta_nao_retornou_resultados'],
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


async def obter_total_os(inicio: date, fim: date, *, unidade_id: int) -> dict:
    """Conta OS criadas no período `[início, fim)`."""
    erro_unidade = validar_unidade_id(unidade_id)
    if erro_unidade:
        return erro_unidade
    erro = _validar_periodo(inicio, fim)
    if erro:
        return erro

    linha = await _consultar(
        """
        SELECT COALESCE(SUM(qtd_os_criadas), 0) AS total_os
        FROM workspace.fixa_pipeline.gold_kpi_os_criacao_diario
        WHERE unidade_id = :unidade_id
          AND data_referencia >= CAST(:inicio AS DATE)
          AND data_referencia < CAST(:fim AS DATE)
        """,
        {**_parametros_periodo(inicio, fim), "unidade_id": unidade_id},
        tipos_parametros={"inicio": "DATE", "fim": "DATE", "unidade_id": "BIGINT"},
    )
    if linha.get("status"):
        return linha
    return _resposta(
        "Total de OS", linha, periodo=_periodo_legivel(inicio, fim),
    )


async def obter_os_abertas(*, unidade_id: int) -> dict:
    """Conta OS atualmente abertas (status 1, 2 ou 3), sem filtro de criação."""
    erro_unidade = validar_unidade_id(unidade_id)
    if erro_unidade:
        return erro_unidade
    linha = await _consultar(
        """
        SELECT COALESCE(SUM(qtd_os), 0) AS os_abertas
        FROM workspace.fixa_pipeline.gold_os_por_status
        WHERE unidade_id = :unidade_id
          AND status_id IN (1, 2, 3)
        """,
        {"unidade_id": unidade_id},
        tipos_parametros={"unidade_id": "BIGINT"},
    )
    if linha.get("status"):
        return linha
    return _resposta("OS abertas", linha)


async def obter_os_atrasadas(*, unidade_id: int) -> dict:
    """Conta OS atualmente classificadas como Atrasada (status 1)."""
    erro_unidade = validar_unidade_id(unidade_id)
    if erro_unidade:
        return erro_unidade
    linha = await _consultar(
        """
        SELECT COALESCE(SUM(qtd_os), 0) AS os_atrasadas
        FROM workspace.fixa_pipeline.gold_os_por_status
        WHERE unidade_id = :unidade_id
          AND status_id = 1
        """,
        {"unidade_id": unidade_id},
        tipos_parametros={"unidade_id": "BIGINT"},
    )
    if linha.get("status"):
        return linha
    return _resposta("OS atrasadas", linha)


async def obter_taxa_atraso_os(*, unidade_id: int) -> dict:
    """Calcula a parcela de OS atrasadas entre as OS abertas no snapshot atual."""
    erro_unidade = validar_unidade_id(unidade_id)
    if erro_unidade:
        return erro_unidade
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
        FROM workspace.fixa_pipeline.gold_os_por_status
        WHERE unidade_id = :unidade_id
        """,
        {"unidade_id": unidade_id},
        tipos_parametros={"unidade_id": "BIGINT"},
    )
    if linha.get("status"):
        return linha
    return _resposta("Taxa de atraso de OS", linha, campo_sem_base="taxa_pct")


async def obter_os_finalizadas(inicio: date, fim: date, *, unidade_id: int) -> dict:
    """Conta OS atualmente finalizadas, por data de conclusão em `[início, fim)`."""
    erro_unidade = validar_unidade_id(unidade_id)
    if erro_unidade:
        return erro_unidade
    erro = _validar_periodo(inicio, fim)
    if erro:
        return erro

    linha = await _consultar(
        """
        SELECT COALESCE(SUM(qtd_os_finalizadas), 0) AS os_finalizadas
        FROM workspace.fixa_pipeline.gold_kpi_os_conclusao_diario
        WHERE unidade_id = :unidade_id
          AND data_referencia >= CAST(:inicio AS DATE)
          AND data_referencia < CAST(:fim AS DATE)
        """,
        {**_parametros_periodo(inicio, fim), "unidade_id": unidade_id},
        tipos_parametros={"inicio": "DATE", "fim": "DATE", "unidade_id": "BIGINT"},
    )
    if linha.get("status"):
        return linha
    return _resposta(
        "OS finalizadas", linha, periodo=_periodo_legivel(inicio, fim),
    )


async def obter_taxa_conclusao_prazo(inicio: date, fim: date, *, unidade_id: int) -> dict:
    """Calcula a conclusão no prazo entre OS finalizadas elegíveis no período."""
    erro_unidade = validar_unidade_id(unidade_id)
    if erro_unidade:
        return erro_unidade
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
        FROM workspace.fixa_pipeline.gold_kpi_os_conclusao_diario
        WHERE unidade_id = :unidade_id
          AND data_referencia >= CAST(:inicio AS DATE)
          AND data_referencia < CAST(:fim AS DATE)
        """,
        {**_parametros_periodo(inicio, fim), "unidade_id": unidade_id},
        tipos_parametros={"inicio": "DATE", "fim": "DATE", "unidade_id": "BIGINT"},
    )
    if linha.get("status"):
        return linha
    return _resposta(
        "Taxa de conclusão no prazo",
        linha,
        periodo=_periodo_legivel(inicio, fim),
        campo_sem_base="taxa_pct",
    )


async def obter_tempo_medio_espera_os(inicio: date, fim: date, *, unidade_id: int) -> dict:
    """Calcula a espera válida até o início das OS criadas no período."""
    erro_unidade = validar_unidade_id(unidade_id)
    if erro_unidade:
        return erro_unidade
    erro = _validar_periodo(inicio, fim)
    if erro:
        return erro

    inicio_timestamp = datetime.combine(inicio, time.min)
    fim_timestamp = datetime.combine(fim, time.min)
    linha = await _consultar(
        """
        SELECT COUNT(*) AS os_com_espera_valida,
               AVG(tempo_espera_minutos) AS media_minutos
        FROM workspace.fixa_pipeline.gold_os_tempos
        WHERE unidade_id = :unidade_id
          AND data_criacao >= :inicio AND data_criacao < :fim
          AND data_inicio >= data_criacao
          AND tempo_espera_minutos IS NOT NULL AND tempo_espera_minutos >= 0
        """,
        {"inicio": inicio_timestamp, "fim": fim_timestamp, "unidade_id": unidade_id},
        tipos_parametros={"inicio": "TIMESTAMP", "fim": "TIMESTAMP", "unidade_id": "BIGINT"},
    )
    if linha.get("status"):
        return linha
    return _resposta(
        "Tempo médio de espera de OS",
        linha,
        periodo=_periodo_legivel(inicio, fim),
        campo_sem_base="media_minutos",
    )
async def obter_tempo_medio_resolucao_os(inicio: date, fim: date, *, unidade_id: int) -> dict:
    """Calcula a resolucao valida das OS concluidas no periodo."""
    erro_unidade = validar_unidade_id(unidade_id)
    if erro_unidade:
        return erro_unidade
    erro = _validar_periodo(inicio, fim)
    if erro:
        return erro
    inicio_ts = datetime.combine(inicio, time.min)
    fim_ts = datetime.combine(fim, time.min)
    linha = await _consultar(
        """
        SELECT COUNT(*) AS os_com_resolucao_valida,
               AVG(tempo_resolucao_minutos) AS media_minutos
        FROM workspace.fixa_pipeline.gold_os_tempos
        WHERE unidade_id = :unidade_id
          AND data_conclusao >= :inicio AND data_conclusao < :fim
          AND status_id = 4
          AND data_inicio >= data_criacao AND data_conclusao >= data_inicio
          AND tempo_resolucao_minutos IS NOT NULL AND tempo_resolucao_minutos >= 0
        """,
        {"inicio": inicio_ts, "fim": fim_ts, "unidade_id": unidade_id},
        tipos_parametros={"inicio": "TIMESTAMP", "fim": "TIMESTAMP", "unidade_id": "BIGINT"},
    )
    if linha.get("status"):
        return linha
    return _resposta("Tempo medio de resolucao de OS", linha,
        periodo=_periodo_legivel(inicio, fim), campo_sem_base="media_minutos")


async def obter_tempo_medio_pausado_os(inicio: date, fim: date, *, unidade_id: int) -> dict:
    """Calcula tempo pausado valido nas OS criadas no periodo, incluindo zero."""
    erro_unidade = validar_unidade_id(unidade_id)
    if erro_unidade:
        return erro_unidade
    erro = _validar_periodo(inicio, fim)
    if erro:
        return erro
    inicio_ts = datetime.combine(inicio, time.min)
    fim_ts = datetime.combine(fim, time.min)
    linha = await _consultar(
        """
        SELECT COUNT(*) AS os_com_tempo_pausado_valido,
               AVG(tempo_pausado_minutos) AS media_minutos
        FROM workspace.fixa_pipeline.gold_os_tempos
        WHERE unidade_id = :unidade_id
          AND data_criacao >= :inicio AND data_criacao < :fim
          AND tempo_pausado_minutos IS NOT NULL AND tempo_pausado_minutos >= 0
        """,
        {"inicio": inicio_ts, "fim": fim_ts, "unidade_id": unidade_id},
        tipos_parametros={"inicio": "TIMESTAMP", "fim": "TIMESTAMP", "unidade_id": "BIGINT"},
    )
    if linha.get("status"):
        return linha
    return _resposta("Tempo medio pausado de OS", linha,
        periodo=_periodo_legivel(inicio, fim), campo_sem_base="media_minutos")


async def _obter_taxa_coorte(
    inicio: date, fim: date, campo: str, indicador: str, *, unidade_id: int,
) -> dict:
    erro_unidade = validar_unidade_id(unidade_id)
    if erro_unidade:
        return erro_unidade
    erro = _validar_periodo(inicio, fim)
    if erro:
        return erro
    linha = await _consultar(
        f"""
        SELECT COALESCE(SUM({campo}), 0) AS numerador,
               COALESCE(SUM(qtd_os_criadas), 0) AS os_criadas,
               100.0 * SUM({campo}) / NULLIF(SUM(qtd_os_criadas), 0) AS taxa_pct
        FROM workspace.fixa_pipeline.gold_kpi_os_criacao_diario
        WHERE unidade_id = :unidade_id
          AND data_referencia >= CAST(:inicio AS DATE)
          AND data_referencia < CAST(:fim AS DATE)
        """,
        {**_parametros_periodo(inicio, fim), "unidade_id": unidade_id},
        tipos_parametros={"inicio": "DATE", "fim": "DATE", "unidade_id": "BIGINT"},
    )
    if linha.get("status"):
        return linha
    return _resposta(indicador, linha, periodo=_periodo_legivel(inicio, fim),
        campo_sem_base="taxa_pct")


async def obter_taxa_reabertura_os(inicio: date, fim: date, *, unidade_id: int) -> dict:
    return await _obter_taxa_coorte(
        inicio, fim, "qtd_os_reabertas", "Taxa de reabertura de OS",
        unidade_id=unidade_id,
    )


async def obter_taxa_reatribuicao_os(inicio: date, fim: date, *, unidade_id: int) -> dict:
    return await _obter_taxa_coorte(
        inicio, fim, "qtd_os_reatribuidas", "Taxa de reatribuicao de OS",
        unidade_id=unidade_id,
    )


async def obter_carga_ativa_tecnicos(*, unidade_id: int) -> dict:
    erro_unidade = validar_unidade_id(unidade_id)
    if erro_unidade:
        return erro_unidade
    linhas = await _consultar_linhas(
        """
        SELECT tecnico_id, tecnico_nome,
               COALESCE(SUM(qtd_os_ativas), 0) AS os_abertas
        FROM workspace.fixa_pipeline.gold_kpi_carga_ativa_tecnico
        WHERE unidade_id = :unidade_id
        GROUP BY tecnico_id, tecnico_nome
        ORDER BY os_abertas DESC, tecnico_id
        """,
        {"unidade_id": unidade_id},
        tipos_parametros={"unidade_id": "BIGINT"},
    )
    if isinstance(linhas, dict):
        return linhas
    return _resposta("Carga ativa por tecnico", linhas)


async def obter_produtividade_tecnicos(inicio: date, fim: date, *, unidade_id: int) -> dict:
    erro_unidade = validar_unidade_id(unidade_id)
    if erro_unidade:
        return erro_unidade
    erro = _validar_periodo(inicio, fim)
    if erro:
        return erro
    linhas = await _consultar_linhas(
        """
        SELECT tecnico_id, tecnico_nome,
               COALESCE(SUM(qtd_os_finalizadas), 0) AS os_finalizadas
        FROM workspace.fixa_pipeline.gold_kpi_produtividade_tecnico
        WHERE unidade_id = :unidade_id
          AND data_referencia >= CAST(:inicio AS DATE)
          AND data_referencia < CAST(:fim AS DATE)
        GROUP BY tecnico_id, tecnico_nome
        ORDER BY os_finalizadas DESC, tecnico_id
        """,
        {**_parametros_periodo(inicio, fim), "unidade_id": unidade_id},
        tipos_parametros={"inicio": "DATE", "fim": "DATE", "unidade_id": "BIGINT"},
    )
    if isinstance(linhas, dict):
        return linhas
    return _resposta("Produtividade por tecnico", linhas,
        periodo=_periodo_legivel(inicio, fim))


async def obter_media_tarefas_por_os(inicio: date, fim: date, *, unidade_id: int) -> dict:
    erro_unidade = validar_unidade_id(unidade_id)
    if erro_unidade:
        return erro_unidade
    erro = _validar_periodo(inicio, fim)
    if erro:
        return erro
    return {
        "status": "INDICADOR_INDISPONIVEL",
        "indicador": "Média de tarefas por OS com tarefas",
        "resultado": {"os_criadas": None, "media_tarefas_por_os": None},
        "periodo": _periodo_legivel(inicio, fim),
        "mensagem": (
            MENSAGENS['a_media_consolidada_de_tarefas_por_os_esta_indisponivel_ate_a_publicacao']
        ),
    }
