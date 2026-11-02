"""Normalização estrita dos valores e dimensões publicados pelo Databricks."""


import math
import re

from app.core.respostas import MENSAGENS


class ErroRespostaDatabricks(RuntimeError):
    """Resultado incompatível com a consulta executada; não é erro do usuário."""


def campo(linha, campo):
    if campo not in linha:
        raise ErroRespostaDatabricks(MENSAGENS['coluna_esperada_ausente_na_resposta'])
    return linha[campo]


def inteiro(valor, *, nao_negativo=True):
    if type(valor) is int:
        numero = valor
    elif isinstance(valor, str) and re.fullmatch(r"[+-]?\d+", valor.strip()):
        numero = int(valor)
    else:
        raise ErroRespostaDatabricks(MENSAGENS['a_resposta_nao_contem_um_inteiro_valido'])
    if nao_negativo and numero < 0:
        raise ErroRespostaDatabricks(MENSAGENS['a_resposta_contem_uma_contagem_negativa'])
    return numero


def numero(valor):
    if type(valor) not in {int, float, str}:
        raise ErroRespostaDatabricks(MENSAGENS['a_resposta_nao_contem_um_numero_valido'])
    if isinstance(valor, str) and not re.fullmatch(
        r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", valor.strip()
    ):
        raise ErroRespostaDatabricks(MENSAGENS['a_resposta_nao_contem_um_numero_valido'])
    numero = float(valor)
    if not math.isfinite(numero):
        raise ErroRespostaDatabricks(MENSAGENS['a_resposta_contem_uma_medida_nao_finita'])
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
                raise ErroRespostaDatabricks(MENSAGENS['rotulo_incompativel_com_o_esquema'])
        grupo[dimensao] = valor
    return grupo
