"""Seleção das análises cujas regras são definidas pelos serviços de domínio."""

from collections.abc import Mapping
from types import MappingProxyType

from app.schemas.visualizacao import Analise, Fonte
from .resumos import resumir_grupo_pequeno
from .limites import validar_limites_resultado
from . import (
    ocorrencia,
    os_atual,
    os_conclusao,
    os_criacao,
    recorrencia,
    solicitacao,
)


_DOMINIOS = (os_criacao, os_conclusao, os_atual, solicitacao, recorrencia, ocorrencia)


def _reunir_analises() -> Mapping[str, Analise]:
    analises = {}
    for dominio in _DOMINIOS:
        for analise in dominio.ANALISES:
            if analise.id in analises:
                raise ValueError("Identificador de análise duplicado nos serviços.")
            if analise.fonte is not dominio.FONTE:
                raise ValueError("A análise não pertence à fonte do serviço.")
            analises[analise.id] = analise
    return MappingProxyType(analises)


FONTES: Mapping[str, Fonte] = MappingProxyType({
    dominio.FONTE.id: dominio.FONTE for dominio in _DOMINIOS
})
FILTROS_POR_FONTE: Mapping[str, Mapping[str, str]] = MappingProxyType({
    dominio.FONTE.id: dominio.FILTROS for dominio in _DOMINIOS
})
ANALISES: Mapping[str, Analise] = _reunir_analises()


def obter_analise(analise_id: str, *, fonte_id: str | None = None) -> Analise:
    """Seleciona uma análise conhecida, opcionalmente restrita à fonte de uma tool."""
    if not isinstance(analise_id, str) or analise_id not in ANALISES:
        raise ValueError("Análise de visualização não cadastrada.")
    analise = ANALISES[analise_id]
    if fonte_id is not None and analise.fonte.id != fonte_id:
        raise ValueError("A análise não pertence à fonte desta ferramenta.")
    return analise


__all__ = [
    "ANALISES", "FONTES", "obter_analise", "resumir_grupo_pequeno",
    "validar_limites_resultado",
    "FILTROS_POR_FONTE",
]
