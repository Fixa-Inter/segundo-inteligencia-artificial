"""Relógio local para referências e períodos de negócio."""

from datetime import date, datetime
from zoneinfo import ZoneInfo

FUSO_HORARIO = ZoneInfo("America/Sao_Paulo")


def agora_local() -> datetime:
    return datetime.now(FUSO_HORARIO)


def data_atual() -> date:
    return agora_local().date()
