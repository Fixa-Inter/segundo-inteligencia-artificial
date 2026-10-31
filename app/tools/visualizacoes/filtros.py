"""Validação dos argumentos das tools, compartilhada com os serviços."""

from collections.abc import Iterable
from types import MappingProxyType

from app.schemas.visualizacao import (
    Analise, ConsultaVisualizacaoPeriodo, ConsultaVisualizacaoSnapshot,
)
from app.services.visualizacoes import (
    FILTROS_POR_FONTE as _DEFINICOES_FILTROS,
    obter_analise,
)
from app.services.visualizacoes.validacao import (
    MAXIMO_VALORES_POR_FILTRO,
    validar_argumentos_analise,
)


# As definições e os tipos dos campos pertencem ao serviço de cada fonte.
FILTROS_POR_FONTE = MappingProxyType({
    fonte: frozenset(campos) for fonte, campos in _DEFINICOES_FILTROS.items()
})


def validar_campos_filtro(analise_id: str, campos: Iterable[str]) -> None:
    """Rejeita campos não autorizados; não substitui a autorização do usuário."""
    analise = obter_analise(analise_id)
    permitidos = FILTROS_POR_FONTE[analise.fonte.id]
    if any(not isinstance(campo, str) or campo not in permitidos for campo in campos):
        raise ValueError("Filtro não permitido para a fonte desta análise.")


def validar_consulta(
    consulta: ConsultaVisualizacaoPeriodo | ConsultaVisualizacaoSnapshot,
    *,
    fonte_id: str,
) -> Analise:
    """Restringe a análise à fonte da tool e reutiliza a validação do serviço."""
    analise = obter_analise(consulta.analise_id, fonte_id=fonte_id)
    validar_argumentos_analise(
        consulta, analise, _DEFINICOES_FILTROS[fonte_id],
    )
    return analise
