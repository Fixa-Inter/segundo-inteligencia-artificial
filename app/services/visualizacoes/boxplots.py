"""SQL dos boxplots: população completa, resumos e extremos limitados."""

import math
import sys

from app.schemas.visualizacao import (
    Analise, BaseCalculoVisualizacao, DadosBoxplot, GrupoBoxplot, GrupoSemBaseBoxplot,
)
from .normalizacao import ErroRespostaDatabricks, campo, grupo as normalizar_grupo, inteiro, numero
from .limites import MAXIMO_EXTREMOS_POR_GRAFICO, MAXIMO_EXTREMOS_POR_GRUPO, MAXIMO_GRUPOS
from .resumos import MINIMO_REGISTROS_BOXPLOT, resumir_grupo_pequeno


class LimiteBoxplotExcedido(ValueError):
    """O conjunto completo de grupos não cabe no gráfico autorizado."""


def montar_sql_boxplot(analise: Analise, condicoes: list[str]):
    campo = analise.campo_valor
    dimensoes = ", ".join(analise.dimensoes)
    ordem = ", ".join(f"{d} ASC NULLS FIRST" for d in analise.dimensoes)
    vinculo = " AND ".join(f"b.{d} <=> g.{d}" for d in analise.dimensoes)
    finito = f"NOT isnan({campo}) AND ABS({campo}) <= :box_maximo_finito"
    elegivel = f"{finito} AND {campo} >= 0" if analise.excluir_negativos else finito
    negativo = f"CASE WHEN {finito} AND {campo} < 0 THEN 1 ELSE 0 END" if analise.excluir_negativos else "0"

    # Uma linha de estatísticas por grupo, até quatro observações por resumo e
    # no máximo 500 extremos. LIMIT nunca antecede os cálculos da população.
    campos = [
        "tipo_linha", "grupo_indice", "qtd_grupos", *analise.dimensoes,
        "qtd_registros_total", "qtd_registros", "qtd_tempos_negativos_excluidos",
        "qtd_registros_invalidos", "qtd_chaves_invalidas", "minimo", "q1", "mediana", "q3",
        "maximo", "media", "limite_inferior", "limite_superior", "bigode_inferior",
        "bigode_superior", "qtd_extremos_total", "valor", "chave_os", "afastamento",
        "ordem_grupo", "ordem_global",
    ]

    def projetar(valores):
        return ", ".join(f"{valores.get(c, 'NULL')} AS {c}" for c in campos)

    cabecalho = {c: f"g.{c}" for c in [
        "grupo_indice", "qtd_grupos", *analise.dimensoes,
        "qtd_registros_total", "qtd_registros", "qtd_tempos_negativos_excluidos",
        "qtd_registros_invalidos", "minimo", "q1", "mediana", "q3", "maximo", "media",
        "limite_inferior", "limite_superior",
    ]}
    cabecalho.update(tipo_linha="0", qtd_chaves_invalidas="d.qtd_chaves_invalidas")
    cabecalho.update({c: f"h.{c}" for c in ["bigode_inferior", "bigode_superior", "qtd_extremos_total"]})
    extremo = {c: f"e.{c}" for c in [
        "grupo_indice", "valor", "chave_os", "afastamento", "ordem_grupo", "ordem_global",
    ]}
    extremo["tipo_linha"] = "1"
    resumo = {c: f"r.{c}" for c in ["grupo_indice", "valor", "chave_os", "ordem_grupo"]}
    resumo["tipo_linha"] = "2"

    sql = f"""SELECT * FROM (
WITH base AS (
  SELECT {dimensoes}, ordem_servico_id AS chave_os,
    CASE WHEN {elegivel} THEN {campo} END AS valor,
    {negativo} AS negativo,
    CASE WHEN {campo} IS NOT NULL AND NOT ({finito}) THEN 1 ELSE 0 END AS inconsistente
  FROM {analise.fonte.tabela}
  WHERE {' AND '.join(condicoes)}
), diagnostico AS (
  SELECT COUNT(*) - COUNT(DISTINCT chave_os) AS qtd_chaves_invalidas FROM base
), estatisticas AS (
  SELECT {dimensoes}, COUNT(*) AS qtd_registros_total, COUNT(valor) AS qtd_registros,
    COUNT(CASE WHEN negativo = 1 THEN 1 END) AS qtd_tempos_negativos_excluidos,
    COUNT(CASE WHEN inconsistente = 1 THEN 1 END) AS qtd_registros_invalidos,
    MIN(valor) AS minimo, MAX(valor) AS maximo, AVG(valor) AS media,
    percentile_cont(0.25) WITHIN GROUP (ORDER BY valor) AS q1,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY valor) AS mediana,
    percentile_cont(0.75) WITHIN GROUP (ORDER BY valor) AS q3
  FROM base GROUP BY {dimensoes}
), grupos AS (
  SELECT *, ROW_NUMBER() OVER (ORDER BY {ordem}) AS grupo_indice,
    COUNT(*) OVER () AS qtd_grupos FROM estatisticas
), limites AS (
  SELECT *, CASE WHEN qtd_registros >= {MINIMO_REGISTROS_BOXPLOT}
      THEN q1 - 1.5 * (q3 - q1) END AS limite_inferior,
    CASE WHEN qtd_registros >= {MINIMO_REGISTROS_BOXPLOT}
      THEN q3 + 1.5 * (q3 - q1) END AS limite_superior
  FROM grupos WHERE grupo_indice <= {MAXIMO_GRUPOS + 1}
), observacoes AS (
  SELECT g.grupo_indice, g.qtd_registros, g.limite_inferior, g.limite_superior, b.chave_os, b.valor,
    CASE WHEN b.valor < g.limite_inferior THEN g.limite_inferior - b.valor
      WHEN b.valor > g.limite_superior THEN b.valor - g.limite_superior END AS afastamento
  FROM base b JOIN limites g ON {vinculo}
), bigodes AS (
  SELECT grupo_indice,
    MIN(CASE WHEN valor BETWEEN limite_inferior AND limite_superior THEN valor END) AS bigode_inferior,
    MAX(CASE WHEN valor BETWEEN limite_inferior AND limite_superior THEN valor END) AS bigode_superior,
    COUNT(afastamento) AS qtd_extremos_total
  FROM observacoes GROUP BY grupo_indice
), extremos_ordenados AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY grupo_indice
    ORDER BY afastamento DESC, valor ASC, chave_os ASC) AS ordem_grupo
  FROM observacoes WHERE afastamento IS NOT NULL
), candidatos AS (
  SELECT * FROM extremos_ordenados WHERE ordem_grupo <= {MAXIMO_EXTREMOS_POR_GRUPO}
), extremos_globais AS (
  SELECT *, ROW_NUMBER() OVER (
    ORDER BY afastamento DESC, valor ASC, grupo_indice ASC, chave_os ASC) AS ordem_global
  FROM candidatos
), resumos AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY grupo_indice ORDER BY valor ASC, chave_os ASC) AS ordem_grupo
  FROM observacoes WHERE qtd_registros < {MINIMO_REGISTROS_BOXPLOT} AND valor IS NOT NULL
)
SELECT {projetar(cabecalho)}
FROM limites g JOIN bigodes h ON g.grupo_indice = h.grupo_indice CROSS JOIN diagnostico d
UNION ALL
SELECT {projetar(extremo)} FROM extremos_globais e WHERE ordem_global <= {MAXIMO_EXTREMOS_POR_GRAFICO}
UNION ALL
SELECT {projetar(resumo)} FROM resumos r
) resultado ORDER BY grupo_indice, tipo_linha, ordem_grupo"""
    return sql, {"box_maximo_finito": sys.float_info.max}, {"box_maximo_finito": "DOUBLE"}


def normalizar_boxplot(analise, linhas, filtros_permitidos, unidade_id):
    cabecalhos, pontos = {}, []
    for linha in linhas:
        tipo, indice = inteiro(campo(linha, "tipo_linha")), inteiro(campo(linha, "grupo_indice"))
        if tipo == 0:
            quantidade_grupos = inteiro(campo(linha, "qtd_grupos"))
            if quantidade_grupos > MAXIMO_GRUPOS:
                raise LimiteBoxplotExcedido("O gráfico excede 50 grupos; refine os filtros.")
            if indice in cabecalhos:
                raise ErroRespostaDatabricks("Grupo repetido na resposta.")
            cabecalhos[indice] = linha
        elif tipo in {1, 2}:
            pontos.append((tipo, indice, linha))
        else:
            raise ErroRespostaDatabricks("Tipo de linha incompatível com o boxplot.")
    if not cabecalhos or set(cabecalhos) != set(range(1, len(cabecalhos) + 1)):
        raise ErroRespostaDatabricks("Grupos incompletos na resposta.")
    grupos, bases, estatisticas, amostras, vistos = {}, {}, {}, {}, set()
    for indice, linha in sorted(cabecalhos.items()):
        if inteiro(campo(linha, "qtd_grupos")) != len(cabecalhos):
            raise ErroRespostaDatabricks("A quantidade de grupos não corresponde à resposta.")
        if inteiro(campo(linha, "qtd_registros_invalidos")) or inteiro(campo(linha, "qtd_chaves_invalidas")):
            raise ErroRespostaDatabricks("Valores ou chaves de OS incompatíveis com a fonte.")
        dimensoes = normalizar_grupo(analise, linha, filtros_permitidos)
        if "unidade_id" in dimensoes and dimensoes["unidade_id"] != unidade_id:
            raise ErroRespostaDatabricks("A unidade retornada não corresponde ao escopo da consulta.")
        chave_grupo = tuple(dimensoes.items())
        if chave_grupo in vistos:
            raise ErroRespostaDatabricks("Dimensões de grupo repetidas na resposta.")
        vistos.add(chave_grupo)
        base = BaseCalculoVisualizacao(
            qtd_registros_total=inteiro(campo(linha, "qtd_registros_total")),
            qtd_registros_elegiveis=inteiro(campo(linha, "qtd_registros")),
            qtd_tempos_negativos_excluidos=inteiro(campo(linha, "qtd_tempos_negativos_excluidos")),
        )
        if not base.qtd_registros_total:
            raise ErroRespostaDatabricks("Um grupo observado exige registros na fonte.")
        grupos[indice], bases[indice], amostras[indice] = dimensoes, base, []
        campos_estatisticas = [
            "minimo", "q1", "mediana", "q3", "maximo", "media", "limite_inferior",
            "limite_superior", "bigode_inferior", "bigode_superior",
        ]
        valores = {c: campo(linha, c) for c in campos_estatisticas}
        extremos = inteiro(campo(linha, "qtd_extremos_total"))
        n = base.qtd_registros_elegiveis
        if not n:
            if any(v is not None for v in valores.values()) or extremos:
                raise ErroRespostaDatabricks("Grupo sem base contém estatísticas.")
            estatisticas[indice] = {"qtd_extremos_total": 0}
            continue
        for c in campos_estatisticas[:6]:
            valores[c] = numero(valores[c])
        if not 0 <= valores["minimo"] <= valores["q1"] <= valores["mediana"] <= valores["q3"] <= valores["maximo"]:
            raise ErroRespostaDatabricks("Estatísticas incompatíveis com os tempos elegíveis.")
        if not valores["minimo"] <= valores["media"] <= valores["maximo"]:
            raise ErroRespostaDatabricks("Média fora dos extremos observados.")
        if n < MINIMO_REGISTROS_BOXPLOT:
            if any(valores[c] is not None for c in campos_estatisticas[6:]) or extremos:
                raise ErroRespostaDatabricks("Grupo pequeno recebeu estatísticas de boxplot.")
        else:
            for c in campos_estatisticas[6:]:
                valores[c] = numero(valores[c])
            iqr = valores["q3"] - valores["q1"]
            if valores["limite_inferior"] != valores["q1"] - 1.5 * iqr or (
                valores["limite_superior"] != valores["q3"] + 1.5 * iqr
            ):
                raise ErroRespostaDatabricks("Limites não correspondem à regra de 1,5 IQR.")
        estatisticas[indice] = {**valores, "qtd_extremos_total": extremos}

    chaves_os, globais = set(), []
    for tipo, indice, linha in pontos:
        if indice not in grupos:
            raise ErroRespostaDatabricks("Observação sem grupo correspondente.")
        chave_os = inteiro(campo(linha, "chave_os"), nao_negativo=False)
        if chave_os in chaves_os:
            raise ErroRespostaDatabricks("Uma OS foi repetida nas observações retornadas.")
        chaves_os.add(chave_os)
        valor, ordem = numero(campo(linha, "valor")), inteiro(campo(linha, "ordem_grupo"))
        n, stats = bases[indice].qtd_registros_elegiveis, estatisticas[indice]
        if valor < 0 or (tipo == 1) != (n >= MINIMO_REGISTROS_BOXPLOT) or not n:
            raise ErroRespostaDatabricks("Observação incompatível com o grupo.")
        if tipo == 1:
            afastamento = numero(campo(linha, "afastamento"))
            esperado = max(stats["limite_inferior"] - valor, valor - stats["limite_superior"])
            if afastamento != esperado or afastamento <= 0:
                raise ErroRespostaDatabricks("Afastamento incompatível com o extremo.")
            global_ = inteiro(campo(linha, "ordem_global"))
            globais.append((global_, -afastamento, valor, indice, chave_os))
            amostras[indice].append((ordem, -afastamento, valor, chave_os))
        else:
            amostras[indice].append((ordem, valor, chave_os))

    esperado_globais = min(sum(
        min(s["qtd_extremos_total"], MAXIMO_EXTREMOS_POR_GRUPO) for s in estatisticas.values()
    ), MAXIMO_EXTREMOS_POR_GRAFICO)
    if len(globais) != esperado_globais or sorted(g[0] for g in globais) != list(range(1, len(globais) + 1)):
        raise ErroRespostaDatabricks("A seleção global dos extremos está incompleta.")
    if sorted(globais) != sorted(globais, key=lambda g: g[1:]):
        raise ErroRespostaDatabricks("Extremos não estão priorizados pelo afastamento.")
    resultados = []
    for indice, dimensoes in grupos.items():
        base, stats, amostra = bases[indice], estatisticas[indice], sorted(amostras[indice])
        n = base.qtd_registros_elegiveis
        if [p[0] for p in amostra] != list(range(1, len(amostra) + 1)) or amostra != sorted(amostra, key=lambda p: p[1:]):
            raise ErroRespostaDatabricks("Observações do grupo estão incompletas ou fora de ordem.")
        if not n:
            resultado = GrupoSemBaseBoxplot(analise_id=analise.id, grupo=dimensoes, base_calculo=base)
        elif n < MINIMO_REGISTROS_BOXPLOT:
            if len(amostra) != n:
                raise ErroRespostaDatabricks("Resumo sem sua população completa.")
            resultado = resumir_grupo_pequeno(analise, grupo=dimensoes, valores=[p[1] for p in amostra])
            for c in ["minimo", "maximo", "media", "mediana"]:
                if not math.isclose(getattr(resultado, c), stats[c], rel_tol=1e-12, abs_tol=1e-12):
                    raise ErroRespostaDatabricks("Resumo incompatível com as estatísticas da fonte.")
            resultado.base_calculo = base
        else:
            if len(amostra) > min(stats["qtd_extremos_total"], MAXIMO_EXTREMOS_POR_GRUPO):
                raise ErroRespostaDatabricks("A seleção excede os extremos do grupo.")
            resultado = GrupoBoxplot(
                analise_id=analise.id, grupo=dimensoes, qtd_registros=n, base_calculo=base,
                **{c: v for c, v in stats.items() if c != "media"},
                valores_extremos=[p[2] for p in amostra],
                qtd_extremos_omitidos=stats["qtd_extremos_total"] - len(amostra),
            )
        resultados.append(resultado)
    base_total = BaseCalculoVisualizacao(
        qtd_registros_total=sum(b.qtd_registros_total for b in bases.values()),
        qtd_registros_elegiveis=sum(b.qtd_registros_elegiveis for b in bases.values()),
        qtd_tempos_negativos_excluidos=sum(b.qtd_tempos_negativos_excluidos for b in bases.values()),
    )
    return DadosBoxplot(grupos=resultados), base_total
