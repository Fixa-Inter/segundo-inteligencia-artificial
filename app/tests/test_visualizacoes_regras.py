"""Regras analíticas e limites de seleção, sem bancos ou modelos externos."""

from dataclasses import FrozenInstanceError
from pathlib import Path
import re

import pytest

from app.services.visualizacoes import ANALISES, FONTES, obter_analise
from app.tools.visualizacoes import validar_campos_filtro
from app.tools.visualizacoes.filtros import FILTROS_POR_FONTE


def test_catalogo_cobre_exatamente_os_ids_do_sdd():
    documento = Path(__file__).resolve().parents[2] / "docs" / "sdd_visualizacoes.md"
    ids = re.findall(r"^\| (VIS-\d{2}) \|", documento.read_text(encoding="utf-8"), re.M)

    assert len(ids) == len(set(ids)) == 27
    assert set(ANALISES) == set(ids)
    assert {analise.fonte.id for analise in ANALISES.values()} == set(FONTES)
    assert set(FILTROS_POR_FONTE) == set(FONTES)


@pytest.mark.parametrize("identificador", ["VIS-00", "VIS-28", "SELECT * FROM tabela", "", None, []])
def test_selecao_rejeita_analises_fora_do_catalogo(identificador):
    with pytest.raises(ValueError, match="não cadastrada"):
        obter_analise(identificador)


def test_tool_de_uma_fonte_nao_pode_selecionar_analise_de_outra():
    with pytest.raises(ValueError, match="não pertence"):
        obter_analise("VIS-01", fonte_id="os_conclusao")

    assert obter_analise("VIS-01", fonte_id="os_criacao").campo_valor == "qtd_os"


@pytest.mark.parametrize("analise_id", tuple(ANALISES))
@pytest.mark.parametrize("campo", ["unidade_id", "unidade_nome", "instituicao_id", "tabela", "sql"])
def test_filtros_nao_ampliam_escopo_nem_escolhem_sql(analise_id, campo):
    with pytest.raises(ValueError, match="Filtro não permitido"):
        validar_campos_filtro(analise_id, [campo])


@pytest.mark.parametrize("campo", ["status_problema", "status_problema_id"])
def test_status_de_solicitacao_nao_se_aplica_a_recorrencia(campo):
    validar_campos_filtro("VIS-08", [campo])

    with pytest.raises(ValueError, match="Filtro não permitido"):
        validar_campos_filtro("VIS-13", [campo])


@pytest.mark.parametrize("analise_id", ["VIS-03", "VIS-04", "VIS-22"])
def test_snapshot_nao_oferece_data_de_criacao_como_filtro_de_periodo(analise_id):
    fonte = obter_analise(analise_id).fonte
    assert fonte.campo_periodo is None
    assert fonte.campo_snapshot == "data_referencia_snapshot"
    validar_campos_filtro(analise_id, ["tecnico_id", "nome_local"])

    for campo in ("data_referencia", "data_criacao", "inicio", "fim"):
        with pytest.raises(ValueError, match="Filtro não permitido"):
            validar_campos_filtro(analise_id, [campo])


def test_entrada_e_saida_tem_fontes_distintas_e_contagens_corretas():
    entrada = obter_analise("VIS-01")
    saida = obter_analise("VIS-02")

    assert entrada.fonte.tabela != saida.fonte.tabela
    assert entrada.campo_valor == "qtd_os"
    assert saida.campo_valor == "qtd_os_finalizadas"
    assert entrada.agregacao == saida.agregacao == "SUM"
    assert obter_analise("VIS-03").agregacao == "COUNT"


def test_percentuais_sao_medias_em_escala_100_sem_zerar_ausencia():
    percentuais = [analise for analise in ANALISES.values() if analise.escala_percentual is not None]
    assert percentuais
    assert all(analise.campo_valor.endswith("_pct_item") for analise in percentuais)
    assert all(analise.agregacao == "AVG" for analise in percentuais)
    assert all(analise.escala_percentual == 100 for analise in percentuais)
    assert all(analise.excluir_nulos for analise in percentuais)


def test_tempos_excluem_nulos_e_estatistica_pendente_nao_recebe_agregacao():
    tempos = [analise for analise in ANALISES.values() if analise.unidade_medida == "minutos"]
    assert tempos
    assert all(analise.excluir_nulos for analise in tempos)
    assert obter_analise("VIS-16").fonte.id == "os_criacao"

    estatisticas = [
        analise for analise in ANALISES.values()
        if analise.formato_dados in {"histograma", "boxplot"}
    ]
    assert len(estatisticas) == 6
    assert all(analise.agregacao is None for analise in estatisticas)


def test_regras_obrigatorias_preservam_populacao_e_semantica():
    for analise_id in ("VIS-04", "VIS-22"):
        filtros = obter_analise(analise_id).filtros_obrigatorios
        assert [(filtro.campo, filtro.valor) for filtro in filtros] == [("os_aberta", 1)]

    prazo = obter_analise("VIS-20").filtros_obrigatorios
    assert len(prazo) == 1
    assert prazo[0].campo == "datas_prazo_validas"
    assert prazo[0].valor is True
    assert obter_analise("VIS-22").campo_valor == "os_prazo_vencido"
    assert obter_analise("VIS-27").campo_valor == "ocorrencia_alta_prioridade"


def test_boxplot_por_unidade_nao_concede_filtro_de_unidade():
    analise = obter_analise("VIS-15")
    assert "unidade_id" in analise.dimensoes
    with pytest.raises(ValueError, match="Filtro não permitido"):
        validar_campos_filtro(analise.id, ["unidade_id"])


def test_ids_de_recorrencia_preservam_tipo_textual_fornecido_pelo_bi():
    assert FONTES["recorrencia"].ids_textuais == {"local_id", "categoria_equipamento_id"}
    assert FONTES["solicitacao"].ids_textuais == frozenset()


def test_selecao_nao_permite_alterar_o_catalogo_compartilhado():
    with pytest.raises(TypeError):
        ANALISES["VIS-01"] = obter_analise("VIS-02")
    with pytest.raises(TypeError):
        FONTES["os_criacao"] = FONTES["os_conclusao"]
    with pytest.raises(FrozenInstanceError):
        obter_analise("VIS-01").campo_valor = "outro_campo"
    with pytest.raises(AttributeError):
        FILTROS_POR_FONTE["recorrencia"].add("status_problema")
    with pytest.raises(TypeError):
        FILTROS_POR_FONTE["recorrencia"] = FILTROS_POR_FONTE["solicitacao"]
