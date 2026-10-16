"""Referência temporal renovada por turno, independente do fuso do servidor."""

from datetime import datetime
from app.core import FUSO_HORARIO, agora_local


def construir_contexto_temporal(instante: datetime | None = None) -> str:
    if instante is not None and instante.tzinfo is None:
        raise ValueError("O instante deve informar seu fuso horário.")
    agora = agora_local() if instante is None else instante.astimezone(FUSO_HORARIO)
    return (
        "Referência temporal deste turno: "
        f"{agora.isoformat(timespec='seconds')} (America/Sao_Paulo).\n"
        "Use esta referência para hoje, ontem e períodos relativos."
    )
