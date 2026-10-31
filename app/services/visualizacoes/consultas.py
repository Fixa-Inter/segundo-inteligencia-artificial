"""Execução compartilhada de agregados e séries temporais das fontes aprovadas.

As análises e os tipos de filtros são fornecidos pelos módulos de domínio, nunca
pela conversa. A unidade deve ser resolvida pelo servidor antes desta chamada.
"""

from collections.abc import Mapping
from datetime import date, datetime
import logging
from uuid import uuid4

from pydantic import ValidationError

from app.core.tempo import agora_local
from app.schemas.visualizacao import (
    Analise, BaseCalculoVisualizacao, ConsultaVisualizacaoPeriodo, ConsultaVisualizacaoSnapshot,
    DadosCategorias, DadosSerieTemporal, MetadadosConsultaVisualizacao,
    PontoCategoria, PontoSerieTemporal, ResultadoConsultaVisualizacao,
)
from app.services.indicadores.gerais import databricks
from app.services.indicadores.gerais.unidade import validar_unidade_id
from .boxplots import LimiteBoxplotExcedido, montar_sql_boxplot, normalizar_boxplot
from .histogramas import construir_histograma, montar_sql_histograma
from .limites import (
    MAXIMO_GRUPOS, MAXIMO_INTERVALOS_HISTOGRAMA, MAXIMO_PONTOS_SERIE, validar_limites_resultado,
)
from .normalizacao import (
    ErroRespostaDatabricks as _ErroRespostaDatabricks,
    campo as _campo, grupo as _grupo, inteiro as _inteiro, numero as _numero,
)
from .temporais import calendario_consulta, expressao_periodo_sql
from .validacao import validar_argumentos_analise


registrador = logging.getLogger(__name__)


class _LimiteSerieExcedido(ValueError):
    """O calendário completo não cabe nos limites aprovados."""


def _erro(status, mensagem):
    return ResultadoConsultaVisualizacao(status=status, mensagem=mensagem)


def _montar_escopo(analise, consulta, unidade_id, filtros_permitidos):
    parametros = {"unidade_id": unidade_id}
    tipos = {"unidade_id": "BIGINT"}
    condicoes = ["unidade_id = :unidade_id"]
    if isinstance(consulta, ConsultaVisualizacaoPeriodo):
        campo = analise.fonte.campo_periodo
        condicoes.extend([
            f"{campo} >= CAST(:inicio AS DATE)",
            f"{campo} < CAST(:fim AS DATE)",
        ])
        parametros.update(inicio=consulta.periodo.inicio, fim=consulta.periodo.fim)
        tipos.update(inicio="DATE", fim="DATE")

    for indice, (campo, selecao) in enumerate(sorted(consulta.filtros.items())):
        valores = selecao if isinstance(selecao, list) else [selecao]
        marcadores = []
        for posicao, valor in enumerate(valores):
            nome = f"filtro_{indice}_{posicao}"
            parametros[nome] = valor
            tipos[nome] = filtros_permitidos[campo]
            marcadores.append(f":{nome}")
        if len(marcadores) == 1:
            condicoes.append(f"{campo} = {marcadores[0]}")
        else:
            condicoes.append(f"{campo} IN ({', '.join(marcadores)})")

    populacao = []
    for indice, filtro in enumerate(analise.filtros_obrigatorios):
        nome = f"obrigatorio_{indice}"
        populacao.append(f"{filtro.campo} = :{nome}")
        parametros[nome] = filtro.valor
        tipos[nome] = "BOOLEAN" if type(filtro.valor) is bool else "INT"

    return condicoes, populacao, parametros, tipos


def _montar_sql(analise, consulta, unidade_id, filtros_permitidos):
    condicoes, populacao, parametros, tipos = _montar_escopo(
        analise, consulta, unidade_id, filtros_permitidos,
    )
    if analise.formato_dados == "histograma":
        sql, parametros_histograma, tipos_histograma = montar_sql_histograma(
            analise, [*condicoes, *populacao],
        )
        return sql, {**parametros, **parametros_histograma}, {**tipos, **tipos_histograma}
    if analise.formato_dados == "boxplot":
        sql, parametros_boxplot, tipos_boxplot = montar_sql_boxplot(analise, [*condicoes, *populacao])
        return sql, {**parametros, **parametros_boxplot}, {**tipos, **tipos_boxplot}

    medida = analise.campo_valor
    elegibilidade = list(populacao)
    if analise.excluir_negativos:
        elegibilidade.append(f"{medida} >= 0")
    if analise.agregacao == "AVG" and elegibilidade:
        # A população da medida não elimina linhas da base total de cobertura.
        # AVG e COUNT ignoram os nulos, preservando observações reais de zero.
        medida = f"CASE WHEN {' AND '.join(elegibilidade)} THEN {medida} END"
    elif analise.agregacao != "AVG":
        condicoes.extend(populacao)

    campos = list(analise.dimensoes)
    dimensoes_agrupamento = list(analise.dimensoes)
    if analise.formato_dados == "serie_temporal":
        periodo_sql = expressao_periodo_sql(analise.fonte.campo_periodo, consulta.granularidade)
        posicao = campos.index("data_referencia")
        campos[posicao] = f"{periodo_sql} AS data_referencia" if periodo_sql != "data_referencia" else periodo_sql
        # GROUP BY deve usar a expressão, pois o alias coincide com uma coluna
        # da fonte e poderia resolver para os dias originais.
        dimensoes_agrupamento[posicao] = periodo_sql
    campos.append(f"{analise.agregacao}({medida}) AS valor")
    if analise.agregacao == "AVG":
        campos.extend([f"COUNT({medida}) AS qtd_registros", "COUNT(*) AS qtd_registros_total"])
        if analise.excluir_negativos:
            negativos = " AND ".join([*populacao, f"{analise.campo_valor} < 0"])
            campos.append(f"COUNT(CASE WHEN {negativos} THEN 1 END) AS qtd_tempos_negativos_excluidos")
    else:
        campos.append("COUNT(*) AS qtd_registros")
    if analise.fonte.campo_snapshot:
        campos.append(f"MAX({analise.fonte.campo_snapshot}) AS instante_snapshot")
    dimensoes = ", ".join(analise.dimensoes)
    agrupamento = ", ".join(dimensoes_agrupamento)
    maximo = MAXIMO_PONTOS_SERIE if analise.formato_dados == "serie_temporal" else MAXIMO_GRUPOS
    # Uma linha além do limite permite recusar excesso sem apresentar um recorte.
    sql = (
        f"SELECT {', '.join(campos)}\n"
        f"FROM {analise.fonte.tabela}\n"
        f"WHERE {' AND '.join(condicoes)}\n"
        f"GROUP BY {agrupamento}\nORDER BY {dimensoes}\nLIMIT {maximo + 1}"
    )
    return sql, parametros, tipos


def _data(valor):
    if type(valor) is date:
        return valor
    if isinstance(valor, str) and len(valor) == 10:
        try:
            return date.fromisoformat(valor)
        except ValueError:
            pass
    raise _ErroRespostaDatabricks("A resposta não contém uma data válida.")


def _medida(analise, linha):
    quantidade = _inteiro(_campo(linha, "qtd_registros"))
    valor = _campo(linha, "valor")
    if analise.agregacao != "AVG":
        return {"valor": _inteiro(valor), "qtd_registros": quantidade}

    base = BaseCalculoVisualizacao(
        qtd_registros_total=_inteiro(_campo(linha, "qtd_registros_total")),
        qtd_registros_elegiveis=quantidade,
        qtd_tempos_negativos_excluidos=(
            _inteiro(_campo(linha, "qtd_tempos_negativos_excluidos"))
            if analise.excluir_negativos else 0
        ),
    )
    if base.qtd_registros_total == 0:
        raise _ErroRespostaDatabricks("Um agrupamento retornado exige registros na fonte.")
    if (valor is None) != (quantidade == 0):
        raise _ErroRespostaDatabricks("A medida não corresponde à base elegível.")
    if valor is not None:
        valor = _numero(valor)
        if analise.escala_percentual is not None and not 0 <= valor <= analise.escala_percentual:
            raise _ErroRespostaDatabricks("O percentual retornado está fora da escala publicada.")
        if analise.excluir_negativos and valor < 0:
            raise _ErroRespostaDatabricks("A média contém tempos negativos excluídos da população.")
    return {"valor": valor, "qtd_registros": quantidade, "base_calculo": base}


def _instante(valor):
    if valor is None or isinstance(valor, datetime):
        return valor
    if isinstance(valor, str):
        try:
            return datetime.fromisoformat(valor.replace("Z", "+00:00"))
        except ValueError:
            pass
    raise _ErroRespostaDatabricks("A resposta não contém um timestamp válido.")


def _categorias(analise, linhas, filtros_permitidos):
    pontos = []
    instantes = []
    grupos_vistos = set()
    for linha in linhas:
        grupo = _grupo(analise, linha, filtros_permitidos)
        chave = tuple(grupo.items())
        if chave in grupos_vistos:
            raise _ErroRespostaDatabricks("A resposta repete um agrupamento de categorias.")
        grupos_vistos.add(chave)
        pontos.append(PontoCategoria(grupo=grupo, **_medida(analise, linha)))
        if analise.fonte.campo_snapshot:
            instante = _instante(_campo(linha, "instante_snapshot"))
            if instante is not None:
                instantes.append(instante)
    return DadosCategorias(pontos=pontos), max(instantes) if instantes else None


def _serie_temporal(analise, linhas, filtros_permitidos, calendario):
    por_data_grupo = {}
    grupos = {}
    for linha in linhas:
        referencia = _data(_campo(linha, "data_referencia"))
        if referencia not in calendario:
            raise _ErroRespostaDatabricks("A resposta contém referência incompatível com o calendário consultado.")
        grupo = _grupo(analise, linha, filtros_permitidos, temporal=True)
        chave_grupo = tuple(grupo.items())
        chave_ponto = (referencia, chave_grupo)
        if chave_ponto in por_data_grupo:
            raise _ErroRespostaDatabricks("A resposta repete um agrupamento temporal.")
        grupos[chave_grupo] = grupo
        por_data_grupo[chave_ponto] = PontoSerieTemporal(
            data_referencia=referencia, periodo=calendario[referencia], grupo=grupo, **_medida(analise, linha),
        )
    if len(grupos) > MAXIMO_GRUPOS:
        raise _LimiteSerieExcedido("A série excede 50 grupos; refine os filtros.")
    if len(calendario) * len(grupos) > MAXIMO_PONTOS_SERIE:
        raise _LimiteSerieExcedido(
            "A série com as lacunas excede 500 pontos; reduza o período ou refine os filtros."
        )

    # Os tipos de cada dimensão já foram normalizados. O marcador de nulidade
    # permite ordenar sem comparar None com inteiros ou nomes.
    chaves = sorted(grupos, key=lambda chave: tuple((valor is not None, valor) for _, valor in chave))
    pontos = []
    for referencia, periodo in calendario.items():
        for chave in chaves:
            ponto = por_data_grupo.get((referencia, chave))
            if ponto is None:
                ponto = PontoSerieTemporal(
                    data_referencia=referencia, periodo=periodo, grupo=grupos[chave],
                    valor=None if analise.agregacao == "AVG" else 0, qtd_registros=0,
                    base_calculo=(
                        BaseCalculoVisualizacao(qtd_registros_total=0, qtd_registros_elegiveis=0)
                        if analise.agregacao == "AVG" else None
                    ),
                )
            pontos.append(ponto)
    return DadosSerieTemporal(pontos=pontos)


def _metadados(analise, consulta, unidade_id, quantidade, instante_snapshot=None, base_calculo=None):
    aplicados = {**consulta.filtros, "unidade_id": unidade_id}
    aplicados.update({filtro.campo: filtro.valor for filtro in analise.filtros_obrigatorios})
    historica = isinstance(consulta, ConsultaVisualizacaoPeriodo)
    return MetadadosConsultaVisualizacao(
        analise_id=analise.id, fonte=analise.fonte.tabela,
        formato_dados=analise.formato_dados, campo_valor=analise.campo_valor,
        agregacao=analise.agregacao, unidade_medida=analise.unidade_medida,
        escala_percentual=analise.escala_percentual,
        periodo=consulta.periodo if historica else None,
        granularidade=consulta.granularidade if historica else None,
        instante_snapshot=instante_snapshot,
        consultado_em=agora_local(), consulta_id=str(uuid4()),
        filtros_solicitados=consulta.filtros, filtros_aplicados=aplicados,
        qtd_registros_considerados=quantidade,
        base_calculo=base_calculo,
    )


def _base_total(dados):
    return BaseCalculoVisualizacao(
        qtd_registros_total=sum(p.base_calculo.qtd_registros_total for p in dados.pontos),
        qtd_registros_elegiveis=sum(p.qtd_registros for p in dados.pontos),
        qtd_tempos_negativos_excluidos=sum(
            p.base_calculo.qtd_tempos_negativos_excluidos for p in dados.pontos
        ),
    )


def _histograma(analise, linhas):
    if len(linhas) != 1:
        raise _ErroRespostaDatabricks("O agregado do histograma exige uma linha.")
    linha = linhas[0]
    if _inteiro(_campo(linha, "qtd_registros_invalidos")):
        raise _ErroRespostaDatabricks("A fonte contém valores incompatíveis com o histograma.")
    base = BaseCalculoVisualizacao(
        qtd_registros_total=_inteiro(_campo(linha, "qtd_registros_total")),
        qtd_registros_elegiveis=_inteiro(_campo(linha, "qtd_registros")),
        qtd_tempos_negativos_excluidos=_inteiro(_campo(linha, "qtd_tempos_negativos_excluidos")),
    )
    if not analise.excluir_negativos and base.qtd_tempos_negativos_excluidos:
        raise _ErroRespostaDatabricks("Exclusões incompatíveis com a população da análise.")
    frequencias = [
        _inteiro(_campo(linha, f"frequencia_{indice}"))
        for indice in range(MAXIMO_INTERVALOS_HISTOGRAMA)
    ]
    minimo, maximo = _campo(linha, "minimo"), _campo(linha, "maximo")
    if not base.qtd_registros_elegiveis:
        if minimo is not None or maximo is not None or any(frequencias):
            raise _ErroRespostaDatabricks("Distribuição sem base contém valores ou frequências.")
        return None, base
    return construir_histograma(
        _numero(minimo), _numero(maximo), frequencias, base.qtd_registros_elegiveis,
    ), base


def _avisos_base(base, analise):
    avisos = []
    if base.qtd_registros_elegiveis < base.qtd_registros_total:
        complemento = (
            "os demais não integram o histograma."
            if analise.formato_dados == "histograma"
            else "os demais não integram as estatísticas dos grupos."
            if analise.formato_dados == "boxplot"
            else "os demais não integram a média. Consulte também a base de cada ponto."
        )
        avisos.append(
            f"Base elegível: {base.qtd_registros_elegiveis} de {base.qtd_registros_total} registros; "
            f"{complemento}"
        )
    if base.qtd_tempos_negativos_excluidos:
        avisos.append(
            f"Tempos negativos excluídos: {base.qtd_tempos_negativos_excluidos}."
        )
    return avisos


async def consultar_agregado(
    consulta: ConsultaVisualizacaoPeriodo | ConsultaVisualizacaoSnapshot,
    *,
    unidade_id: int,
    analises: tuple[Analise, ...],
    filtros_permitidos: Mapping[str, str],
    implementadas: frozenset[str],
) -> ResultadoConsultaVisualizacao:
    from time import perf_counter
    from app.observability.metricas import CONSULTAS_VISUALIZACAO, DURACAO_CONSULTAS_VISUALIZACAO

    inicio = perf_counter()
    identificador = getattr(consulta, "analise_id", None)
    identificador = identificador if type(identificador) is str and identificador in {a.id for a in analises} else "desconhecida"
    status = "ERRO_FERRAMENTA"
    try:
        resultado = await _consultar_agregado(
            consulta, unidade_id=unidade_id, analises=analises,
            filtros_permitidos=filtros_permitidos, implementadas=implementadas,
        )
        status = resultado.status
        return resultado
    finally:
        CONSULTAS_VISUALIZACAO.labels(identificador, status).inc()
        DURACAO_CONSULTAS_VISUALIZACAO.labels(identificador, status).observe(perf_counter() - inicio)


async def _consultar_agregado(
    consulta: ConsultaVisualizacaoPeriodo | ConsultaVisualizacaoSnapshot,
    *,
    unidade_id: int,
    analises: tuple[Analise, ...],
    filtros_permitidos: Mapping[str, str],
    implementadas: frozenset[str],
) -> ResultadoConsultaVisualizacao:
    """Executa análise registrada pelo domínio, com validação antes da consulta."""
    if validar_unidade_id(unidade_id):
        return _erro("ERRO_VALIDACAO", "Unidade inválida para consultar visualizações.")
    try:
        if not isinstance(consulta, (ConsultaVisualizacaoPeriodo, ConsultaVisualizacaoSnapshot)):
            raise ValueError("Informe uma consulta de visualização válida.")
        # Revalida e copia os argumentos antes do await, preservando a consulta e
        # os metadados mesmo que o objeto do chamador seja alterado em paralelo.
        consulta = type(consulta).model_validate(consulta.model_dump())
        analise = next((item for item in analises if item.id == consulta.analise_id), None)
        if analise is None:
            raise ValueError("A análise não pertence à fonte deste serviço.")
        validar_argumentos_analise(consulta, analise, filtros_permitidos)
        if analise.id not in implementadas:
            raise ValueError("Esta análise ainda não está implementada neste serviço.")
        calendario = None
        if analise.formato_dados == "serie_temporal":
            if "data_referencia" not in analise.dimensoes:
                raise ValueError("A série exige uma dimensão temporal canônica.")
            calendario = calendario_consulta(consulta.periodo, consulta.granularidade)
        if analise.formato_dados not in {"histograma", "boxplot"} and analise.agregacao not in {"SUM", "COUNT", "AVG"}:
            raise ValueError("Esta agregação ainda não está implementada neste serviço.")
        sql, parametros, tipos = _montar_sql(analise, consulta, unidade_id, filtros_permitidos)
    except (ValidationError, TypeError):
        return _erro("ERRO_VALIDACAO", "Consulta inválida ou ainda indisponível; confira análise, período e filtros.")
    except ValueError as erro:
        return _erro("ERRO_VALIDACAO", str(erro))

    try:
        linhas = await databricks.executar_consulta(sql, parametros, tipos_parametros=tipos)
    except databricks.TimeoutConsultaDatabricks:
        return _erro("TIMEOUT", "A consulta excedeu o tempo limite; reduza o período ou refine os filtros.")
    except databricks.ResultadoDatabricksTruncado:
        return _erro("RESULTADO_TRUNCADO", "O resultado excedeu o limite de transporte; refine os filtros.")
    except Exception as erro:
        registrador.error("Falha na consulta %s: %s", analise.id, type(erro).__name__)
        return _erro("ERRO_FERRAMENTA", "Não foi possível consultar os dados no Databricks.")

    try:
        if not isinstance(linhas, list) or any(not isinstance(linha, Mapping) for linha in linhas):
            raise _ErroRespostaDatabricks("Formato de resposta incompatível.")
        if not linhas and analise.formato_dados != "histograma":
            return ResultadoConsultaVisualizacao(
                status="SEM_RESULTADO", mensagem="A consulta não retornou dados para esta análise.",
                metadados=_metadados(
                    analise, consulta, unidade_id, 0,
                    base_calculo=(
                        BaseCalculoVisualizacao(qtd_registros_total=0, qtd_registros_elegiveis=0)
                        if analise.agregacao == "AVG" or analise.formato_dados == "boxplot" else None
                    ),
                ),
            )
        if analise.formato_dados == "histograma":
            dados, base = _histograma(analise, linhas)
            metadados = _metadados(
                analise, consulta, unidade_id, base.qtd_registros_elegiveis, base_calculo=base,
            )
            if dados is None:
                return ResultadoConsultaVisualizacao(
                    status="SEM_BASE_CALCULO" if base.qtd_registros_total else "SEM_RESULTADO",
                    mensagem="Não há observações elegíveis para o histograma.",
                    metadados=metadados, avisos=_avisos_base(base, analise),
                )
        elif analise.formato_dados == "boxplot":
            dados, base = normalizar_boxplot(analise, linhas, filtros_permitidos, unidade_id)
            metadados = _metadados(
                analise, consulta, unidade_id, base.qtd_registros_elegiveis, base_calculo=base,
            )
        elif analise.formato_dados == "serie_temporal":
            dados = _serie_temporal(analise, linhas, filtros_permitidos, calendario)
            instante = None
        else:
            dados, instante = _categorias(analise, linhas, filtros_permitidos)
        if analise.formato_dados not in {"histograma", "boxplot"}:
            quantidade = sum(ponto.qtd_registros for ponto in dados.pontos)
            base = _base_total(dados) if analise.agregacao == "AVG" else None
            metadados = _metadados(analise, consulta, unidade_id, quantidade, instante, base)
    except (_LimiteSerieExcedido, LimiteBoxplotExcedido) as erro:
        return _erro("ERRO_VALIDACAO", str(erro))
    except Exception as erro:
        registrador.error("Resposta incompatível na consulta %s: %s", analise.id, type(erro).__name__)
        return _erro("ERRO_FERRAMENTA", "O Databricks retornou dados incompatíveis com a análise.")

    try:
        validar_limites_resultado(dados)
    except ValueError as erro:
        return _erro("ERRO_VALIDACAO", str(erro))
    avisos = _avisos_base(base, analise) if base is not None else []
    if analise.formato_dados == "boxplot":
        omitidos = sum(getattr(g, "qtd_extremos_omitidos", 0) for g in dados.grupos)
        if omitidos:
            avisos.append(
                f"Pontos extremos omitidos pelos limites de retorno: {omitidos}. "
                "Estatísticas e contagens usam toda a população elegível."
            )
    if base is not None and base.qtd_registros_elegiveis == 0:
        return ResultadoConsultaVisualizacao(
            status="SEM_BASE_CALCULO", mensagem="Há registros no recorte, mas nenhum é elegível para a medida.",
            metadados=metadados, avisos=avisos,
        )
    mensagem = "Consulta concluída."
    if isinstance(dados, DadosSerieTemporal) and any(p.periodo.parcial for p in dados.pontos):
        mensagem = "Consulta concluída; períodos parciais identificados nos pontos."
    return ResultadoConsultaVisualizacao(
        status="SUCESSO_PARCIAL" if avisos else "SUCESSO", mensagem=mensagem,
        metadados=metadados, dados=dados, avisos=avisos,
    )
