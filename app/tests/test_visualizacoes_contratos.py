"""Contratos analíticos e validação das futuras tools, sem consultas externas."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas.visualizacao import (
    ConsultaVisualizacaoPeriodo, ConsultaVisualizacaoSnapshot, DadosBoxplot,
    DadosCategorias, DadosHistograma, DadosSerieTemporal, GrupoBoxplot,
    IntervaloHistograma, MetadadosConsultaVisualizacao, PeriodoVisualizacao,
    PontoCategoria, PontoSerieTemporal, ResultadoConsultaVisualizacao,
)
from app.services.visualizacoes import obter_analise, resumir_grupo_pequeno
from app.tools.visualizacoes import validar_consulta


PERIODO = {"inicio": "2026-10-01", "fim": "2026-11-01"}


def consulta(analise_id="VIS-01", *, filtros=None, granularidade="dia"):
    return ConsultaVisualizacaoPeriodo(
        analise_id=analise_id, periodo=PERIODO,
        filtros=filtros or {}, granularidade=granularidade,
    )


def metadados(analise_id="VIS-01"):
    analise = obter_analise(analise_id)
    return MetadadosConsultaVisualizacao(
        analise_id=analise.id, fonte=analise.fonte.tabela,
        formato_dados=analise.formato_dados, campo_valor=analise.campo_valor,
        agregacao=analise.agregacao, unidade_medida=analise.unidade_medida,
        escala_percentual=analise.escala_percentual, periodo=PERIODO,
        granularidade="dia" if analise.formato_dados == "serie_temporal" else None,
        consultado_em=datetime(2026, 10, 30, 12, tzinfo=timezone.utc),
        consulta_id="consulta-teste", qtd_registros_considerados=5,
    )


def grupo_boxplot(**alteracoes):
    dados = {
        "analise_id": "VIS-17", "grupo": {"tipo_local": "Sala"},
        "qtd_registros": 5, "minimo": 1, "q1": 2, "mediana": 3, "q3": 4,
        "maximo": 100, "limite_inferior": -1, "limite_superior": 7,
        "bigode_inferior": 1, "bigode_superior": 4,
        "valores_extremos": [100], "qtd_extremos_total": 1,
        "qtd_extremos_omitidos": 0,
    }
    return GrupoBoxplot(**{**dados, **alteracoes})


def test_periodo_usa_datas_explicitas_e_fim_exclusivo():
    periodo = PeriodoVisualizacao(**PERIODO)
    assert periodo.inicio.isoformat() == "2026-10-01"
    assert periodo.fim.isoformat() == "2026-11-01"


@pytest.mark.parametrize("alteracao", [
    {"fim": "2026-10-01"}, {"fim": "2026-09-30"},
    {"inicio": 0}, {"inicio": "20261001"}, {"inicio": "2026-10-01T00:00:00"},
])
def test_periodo_nao_aceita_intervalo_invalido_ou_timestamp_implicito(alteracao):
    with pytest.raises(ValidationError):
        PeriodoVisualizacao(**{**PERIODO, **alteracao})


@pytest.mark.parametrize("campo", ["unidade_id", "instituicao_id", "sql", "fonte_id"])
def test_contexto_autenticado_e_fonte_nao_sao_argumentos_do_modelo(campo):
    with pytest.raises(ValidationError):
        ConsultaVisualizacaoPeriodo(
            analise_id="VIS-01", periodo=PERIODO, **{campo: "qualquer"},
        )


@pytest.mark.parametrize("campo,valor", [("periodo", PERIODO), ("granularidade", "dia")])
def test_contrato_snapshot_nao_oferece_parametros_temporais(campo, valor):
    with pytest.raises(ValidationError):
        ConsultaVisualizacaoSnapshot(analise_id="VIS-03", **{campo: valor})


def test_validacao_impede_escolha_de_analise_de_outra_tool():
    with pytest.raises(ValueError, match="não pertence"):
        validar_consulta(consulta(), fonte_id="os_conclusao")


def test_validacao_recusa_periodo_no_snapshot_e_exige_periodo_nas_demais_fontes():
    with pytest.raises(ValueError, match="snapshot não aceita período"):
        validar_consulta(consulta("VIS-03"), fonte_id="os_atual")
    with pytest.raises(ValueError, match="exige um período"):
        validar_consulta(ConsultaVisualizacaoSnapshot(analise_id="VIS-01"), fonte_id="os_criacao")


def test_series_exigem_granularidade_e_outros_formatos_nao_a_aceitam():
    with pytest.raises(ValueError, match="Informe a granularidade"):
        validar_consulta(consulta(granularidade=None), fonte_id="os_criacao")
    with pytest.raises(ValueError, match="apenas em séries"):
        validar_consulta(consulta("VIS-06"), fonte_id="os_criacao")


def test_filtros_multiplos_preservam_valores_sem_escolher_outro_escopo():
    dados = consulta(filtros={"local_id": [1, 2], "tecnico_nome": ["Ana", "Bia"]})
    assert validar_consulta(dados, fonte_id="os_criacao").id == "VIS-01"
    assert dados.filtros == {"local_id": [1, 2], "tecnico_nome": ["Ana", "Bia"]}
    with pytest.raises(ValueError, match="Filtro não permitido"):
        validar_consulta(consulta(filtros={"unidade_id": [1, 2]}), fonte_id="os_criacao")


@pytest.mark.parametrize("valor", [[], 1.5, None, {"operador": "OR"}])
def test_contrato_filtro_recusa_selecao_vazia_e_operadores_arbitrarios(valor):
    with pytest.raises(ValidationError):
        consulta(filtros={"local_id": valor})


@pytest.mark.parametrize("filtros", [
    {"tecnico_id": True}, {"tecnico_id": "1"}, {"tecnico_nome": 1},
    {"tecnico_nome": " "}, {"local_id": [1, "2"]},
])
def test_valores_de_filtro_respeitam_tipo_sem_conversao_silenciosa(filtros):
    with pytest.raises(ValueError):
        validar_consulta(consulta(filtros=filtros), fonte_id="os_criacao")


def test_ids_textuais_de_recorrencia_nao_sao_convertidos_em_inteiros():
    dados = consulta("VIS-13", filtros={"local_id": ["001", "002"]}, granularidade=None)
    validar_consulta(dados, fonte_id="recorrencia")
    assert dados.filtros["local_id"] == ["001", "002"]
    with pytest.raises(ValueError, match="texto"):
        validar_consulta(
            consulta("VIS-13", filtros={"local_id": 1}, granularidade=None),
            fonte_id="recorrencia",
        )


def test_filtros_nao_contradizem_populacao_obrigatoria_de_os_abertas():
    for valor in (0, [0, 1]):
        dados = ConsultaVisualizacaoSnapshot(analise_id="VIS-04", filtros={"os_aberta": valor})
        with pytest.raises(ValueError, match="contradiz"):
            validar_consulta(dados, fonte_id="os_atual")
    dados = ConsultaVisualizacaoSnapshot(analise_id="VIS-04", filtros={"os_aberta": [1]})
    assert validar_consulta(dados, fonte_id="os_atual").id == "VIS-04"


def test_flag_booleana_de_ocorrencia_nao_aceita_inteiro_no_lugar_de_booleano():
    dados = consulta("VIS-26", filtros={"esta_ativo": False})
    validar_consulta(dados, fonte_id="ocorrencia")
    with pytest.raises(ValueError, match="booleano"):
        validar_consulta(consulta("VIS-26", filtros={"esta_ativo": 0}), fonte_id="ocorrencia")


def test_contrato_preserva_grupos_nulos_valor_zero_e_ausencia_de_base():
    categoria = PontoCategoria(grupo={"tecnico_id": None, "tecnico_nome": None}, valor=0, qtd_registros=1)
    sem_base = PontoSerieTemporal(data_referencia="2026-10-01", grupo={}, valor=None, qtd_registros=0)
    assert categoria.grupo["tecnico_id"] is None
    assert type(categoria.valor) is int and categoria.valor == 0
    assert sem_base.valor is None


@pytest.mark.parametrize("valor", [True, "10", float("nan"), float("inf")])
def test_medidas_nao_aceitam_booleanos_texto_ou_nao_finitos(valor):
    with pytest.raises(ValidationError):
        PontoCategoria(grupo={}, valor=valor, qtd_registros=1)


def test_histograma_aceita_valor_constante_e_cobra_cobertura_da_populacao():
    intervalo = IntervaloHistograma(inferior=5, superior=5, frequencia=3, inclui_superior=True)
    assert DadosHistograma(intervalos=[intervalo], qtd_registros=3).intervalos[0].superior == 5
    with pytest.raises(ValidationError, match="cobrir a população"):
        DadosHistograma(intervalos=[intervalo], qtd_registros=4)


@pytest.mark.parametrize("alteracao", [
    {"q1": 5}, {"bigode_inferior": -2}, {"valores_extremos": [3]},
    {"qtd_extremos_omitidos": 1}, {"qtd_extremos_total": 6, "qtd_extremos_omitidos": 5},
])
def test_boxplot_rejeita_quartis_bigodes_pontos_e_contagens_inconsistentes(alteracao):
    with pytest.raises(ValidationError):
        grupo_boxplot(**alteracao)


def test_bigodes_observados_nao_sao_forcados_aos_quartis_interpolados():
    resultado = grupo_boxplot(
        qtd_registros=8, minimo=0, q1=75, mediana=100, q3=100,
        limite_inferior=37.5, limite_superior=137.5,
        bigode_inferior=100, bigode_superior=100,
        valores_extremos=[0, 0], qtd_extremos_total=2,
    )
    assert resultado.bigode_inferior > resultado.q1


def test_mesma_analise_pode_retornar_boxplot_e_resumo_em_grupos_distintos():
    resumo = resumir_grupo_pequeno(
        obter_analise("VIS-17"), grupo={"tipo_local": "Oficina"}, valores=[2, 8],
    )
    resultado = ResultadoConsultaVisualizacao(
        status="SUCESSO", mensagem="Consulta concluída.", metadados=metadados("VIS-17"),
        dados=DadosBoxplot(grupos=[grupo_boxplot(), resumo]),
    )
    dados = ResultadoConsultaVisualizacao.model_validate_json(resultado.model_dump_json()).dados
    assert [grupo.tipo for grupo in dados.grupos] == ["boxplot", "resumo"]


@pytest.mark.parametrize("status", [
    "SEM_RESULTADO", "SEM_BASE_CALCULO", "ERRO_VALIDACAO", "ACESSO_NEGADO",
    "ERRO_FERRAMENTA", "TIMEOUT", "RESULTADO_TRUNCADO",
])
def test_resultados_sem_sucesso_nao_liberam_grafico(status):
    assert ResultadoConsultaVisualizacao(status=status, mensagem="Sem dados liberados.").dados is None
    with pytest.raises(ValidationError, match="não podem liberar"):
        ResultadoConsultaVisualizacao(
            status=status, mensagem="Sem dados liberados.", metadados=metadados(),
            dados=DadosSerieTemporal(pontos=[PontoSerieTemporal(
                data_referencia="2026-10-01", grupo={}, valor=1, qtd_registros=1,
            )]),
        )


def test_sucesso_exige_dados_e_metadados_compativeis():
    with pytest.raises(ValidationError, match="exige dados e metadados"):
        ResultadoConsultaVisualizacao(status="SUCESSO", mensagem="Consulta concluída.")
    with pytest.raises(ValidationError, match="não corresponde"):
        ResultadoConsultaVisualizacao(
            status="SUCESSO", mensagem="Consulta concluída.", metadados=metadados(),
            dados=DadosCategorias(pontos=[PontoCategoria(grupo={}, valor=1, qtd_registros=1)]),
        )


def test_grupos_de_boxplot_nao_podem_misturar_analises():
    with pytest.raises(ValidationError, match="pertencer à análise"):
        ResultadoConsultaVisualizacao(
            status="SUCESSO", mensagem="Consulta concluída.", metadados=metadados("VIS-16"),
            dados=DadosBoxplot(grupos=[grupo_boxplot()]),
        )


def test_consulta_tem_fuso_e_metadados_nao_misturam_snapshot_com_periodo():
    dados = metadados().model_dump()
    with pytest.raises(ValidationError, match="fuso"):
        MetadadosConsultaVisualizacao(**{**dados, "consultado_em": datetime(2026, 10, 30)})
    with pytest.raises(ValidationError, match="simultaneamente"):
        MetadadosConsultaVisualizacao(**{**dados, "instante_snapshot": dados["consultado_em"]})
