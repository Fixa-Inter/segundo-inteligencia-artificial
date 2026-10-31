"""Normalização estrita dos valores e dimensões publicados pelo Databricks."""

import math
import re


class ErroRespostaDatabricks(RuntimeError):
    """Resultado incompatível com a consulta executada; não é erro do usuário."""


def campo(linha, campo):
    if campo not in linha:
        raise ErroRespostaDatabricks("Coluna esperada ausente na resposta.")
    return linha[campo]


def inteiro(valor, *, nao_negativo=True):
    if type(valor) is int:
        numero = valor
    elif isinstance(valor, str) and re.fullmatch(r"[+-]?\d+", valor.strip()):
        numero = int(valor)
    else:
        raise ErroRespostaDatabricks("A resposta não contém um inteiro válido.")
    if nao_negativo and numero < 0:
        raise ErroRespostaDatabricks("A resposta contém uma contagem negativa.")
    return numero


def numero(valor):
    if type(valor) not in {int, float, str}:
        raise ErroRespostaDatabricks("A resposta não contém um número válido.")
    if isinstance(valor, str) and not re.fullmatch(
        r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", valor.strip()
    ):
        raise ErroRespostaDatabricks("A resposta não contém um número válido.")
    numero = float(valor)
    if not math.isfinite(numero):
        raise ErroRespostaDatabricks("A resposta contém uma medida não finita.")
    return numero


def grupo(analise, linha, filtros_permitidos, *, temporal=False):
    grupo = {}
    for dimensao in analise.dimensoes:
        if temporal and dimensao == "data_referencia":
            continue
        valor = campo(linha, dimensao)
        if valor is not None:
            tipo = filtros_permitidos.get(dimensao, {"unidade_id": "BIGINT", "unidade_nome": "STRING"}.get(dimensao))
            if tipo in {"INT", "BIGINT"}:
                valor = inteiro(valor, nao_negativo=False)
            elif tipo not in {"STRING", "VARCHAR"} or type(valor) is not str:
                raise ErroRespostaDatabricks("Rótulo incompatível com o esquema.")
        grupo[dimensao] = valor
    return grupo
