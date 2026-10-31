"""Cálculo do resumo e distinção entre grupo pequeno, vazio e boxplot."""

import json

import pytest
from pydantic import ValidationError

from app.schemas.visualizacao import ResumoGrupoPequeno
from app.services.visualizacoes import obter_analise, resumir_grupo_pequeno


def resumir(valores, *, grupo=None):
    return resumir_grupo_pequeno(
        obter_analise("VIS-17"),
        grupo=grupo if grupo is not None else {"tipo_local": "Sala"},
        valores=valores,
    )


@pytest.mark.parametrize(
    ("valores", "media", "mediana"),
    [
        ([12], 12, 12),
        ([8, 2], 5, 5),
        ([10, 20, 60], 30, 20),
        ([40, 0, 8, 12], 15, 10),
    ],
)
def test_calcula_resumo_da_populacao_com_um_a_quatro_registros(valores, media, mediana):
    resultado = resumir(valores)

    assert resultado.qtd_registros == len(valores)
    assert resultado.minimo == min(valores)
    assert resultado.maximo == max(valores)
    assert resultado.media == media
    assert resultado.mediana == mediana
    assert resultado.tipo == "resumo"
    assert resultado.unidade == "minutos"
    assert resultado.motivo == "POUCOS_REGISTROS_PARA_BOXPLOT"


def test_exclui_nulos_preservando_zeros_e_conta_somente_observacoes_validas():
    resultado = resumir([None, 0, 10, None])

    assert resultado.qtd_registros == 2
    assert resultado.minimo == 0
    assert resultado.maximo == 10
    assert resultado.media == resultado.mediana == 5


@pytest.mark.parametrize("valores", [[], [None], [None, None]])
def test_grupo_vazio_nao_ganha_resumo_com_valores_zero(valores):
    assert resumir(valores) is None


@pytest.mark.parametrize("valores", [[0] * 5, [1, 2, 3, 4, 5, None], list(range(20))])
def test_nao_trunca_grupo_elegivel_para_boxplot_para_caber_no_resumo(valores):
    with pytest.raises(ValueError, match="cinco ou mais"):
        resumir(valores)


def test_limite_considera_nao_nulos_e_nao_o_tamanho_da_lista():
    resultado = resumir([None, 1, 2, None, 3, 4, None])
    assert resultado.qtd_registros == 4
    assert resultado.media == resultado.mediana == 2.5


def test_valores_iguais_preservam_ausencia_de_dispersao():
    resultado = resumir([7, 7, 7])
    assert resultado.minimo == resultado.maximo == resultado.media == resultado.mediana == 7


def test_nao_arredonda_observacoes_antes_das_estatisticas():
    resultado = resumir([0.001, 0.002, 0.009])
    assert resultado.minimo == 0.001
    assert resultado.maximo == 0.009
    assert resultado.media == pytest.approx(0.004)
    assert resultado.mediana == 0.002


@pytest.mark.parametrize("valor", [True, "10", float("nan"), float("inf"), float("-inf")])
def test_entrada_invalida_nao_e_descartada_silenciosamente(valor):
    with pytest.raises(ValueError, match="números"):
        resumir([10, valor])


@pytest.mark.parametrize("analise_id", ["VIS-15", "VIS-16", "VIS-17"])
def test_preserva_identidade_e_campos_do_grupo_em_cada_analise(analise_id):
    analise = obter_analise(analise_id)
    grupo = {
        campo: 42 if campo.endswith("_id") else "Grupo de teste"
        for campo in analise.dimensoes
    }
    resultado = resumir_grupo_pequeno(analise, grupo=grupo, valores=[2, 6])

    assert resultado.analise_id == analise_id
    assert resultado.grupo == grupo
    grupo[next(iter(grupo))] = "alterado depois"
    assert resultado.grupo != grupo


def test_nao_inventa_rotulo_para_dimensao_nula():
    assert resumir([5], grupo={"tipo_local": None}).grupo == {"tipo_local": None}


@pytest.mark.parametrize("grupo", [{}, {"nome_local": "Sala"}, {"tipo_local": "Sala", "sql": "x"}])
def test_rejeita_dimensoes_que_nao_correspondem_a_analise(grupo):
    with pytest.raises(ValueError, match="dimensões"):
        resumir([1, 2], grupo=grupo)


def test_resumo_nao_substitui_outros_tipos_de_analise():
    with pytest.raises(ValueError, match="boxplot de tempos"):
        resumir_grupo_pequeno(
            obter_analise("VIS-06"), grupo={}, valores=[1, 2],
        )


def test_serializacao_preserva_identificacao_estatisticas_e_motivo():
    dados = json.loads(resumir([10, 20, 60]).model_dump_json())
    assert dados == {
        "tipo": "resumo",
        "analise_id": "VIS-17",
        "grupo": {"tipo_local": "Sala"},
        "unidade": "minutos",
        "qtd_registros": 3,
        "minimo": 10.0,
        "maximo": 60.0,
        "media": 30.0,
        "mediana": 20.0,
        "motivo": "POUCOS_REGISTROS_PARA_BOXPLOT",
        "base_calculo": None,
    }


@pytest.mark.parametrize(
    "alteracao",
    [
        {"qtd_registros": 0},
        {"qtd_registros": True},
        {"media": 61},
        {"mediana": 9},
        {"media": float("nan")},
        {"unidade": "horas"},
        {"tipo": "boxplot"},
        {"campo_extra": 1},
    ],
)
def test_contrato_rejeita_resumo_inconsistente(alteracao):
    dados = resumir([10, 20, 60]).model_dump()
    with pytest.raises(ValidationError):
        ResumoGrupoPequeno(**{**dados, **alteracao})
