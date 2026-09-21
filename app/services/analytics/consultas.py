from app.schemas.analytics import (
    ComparacaoPeriodosRequest,
    PeriodoRequest,
)


def consultar_analytics_mock(
    indicador: str,
    periodo: PeriodoRequest,
) -> dict:
    return {
        "status": "DADOS_MOCKADOS",
        "fonte": "mock",
        "indicador": indicador,
        "periodo": {
            "inicio": periodo.inicio.isoformat(),
            "fim": periodo.fim.isoformat(),
        },
        "resultado": None,
        "mensagem": (
            "A estrutura do endpoint está pronta, "
            "mas a fonte real de analytics ainda "
            "não foi integrada."
        ),
    }


def comparar_periodos_mock(
    dados: ComparacaoPeriodosRequest,
) -> dict:
    return {
        "status": "DADOS_MOCKADOS",
        "fonte": "mock",
        "indicador": "comparacao_periodos",
        "periodo_atual": {
            "inicio": (
                dados.periodo_atual.inicio.isoformat()
            ),
            "fim": dados.periodo_atual.fim.isoformat(),
        },
        "periodo_anterior": {
            "inicio": (
                dados.periodo_anterior.inicio.isoformat()
            ),
            "fim": (
                dados.periodo_anterior.fim.isoformat()
            ),
        },
        "resultado": None,
        "mensagem": (
            "A estrutura do endpoint está pronta, "
            "mas a fonte real de analytics ainda "
            "não foi integrada."
        ),
    }