"""Relógio local para referências e períodos de negócio."""

from datetime import timezone, date, datetime
from zoneinfo import ZoneInfo

# FUSO_HORARIO: Recurso compartilhado de fuso horario usado pelas funções deste módulo e pela interface pública.
FUSO_HORARIO = ZoneInfo("America/Sao_Paulo")


def agora_local() -> datetime:
    """Devolve datetime atual com o fuso America/Sao_Paulo. Usado por data_atual."""
    return datetime.now(FUSO_HORARIO)


def data_atual() -> date:
    """Devolve a data do relógio de negócio local. Usado pelo fluxo de core."""
    return agora_local().date()


def agora_utc() -> datetime:
    """Relógio UTC usado pela persistência, sem depender de clientes de banco."""
    return datetime.now(timezone.utc)


def data_iso_banco(valor, *, permitir_nulo: bool = False) -> str | None:
    """Normaliza date/datetime de SQL; OS permite None, outros registros não."""
    from app.core import MENSAGENS
    if valor is None and permitir_nulo:
        return None
    if isinstance(valor, datetime):
        return valor.date().isoformat()
    if isinstance(valor, date):
        return valor.isoformat()
    raise ValueError(MENSAGENS['data_retornada_pelo_banco_em_formato_invalido'])


def subtrair_meses(hoje: date, meses: int) -> date:
    """Subtrai meses de calendário, ajustando dias inexistentes no mês de destino."""
    from calendar import monthrange
    indice_mes = hoje.year * 12 + hoje.month - 1 - meses
    ano, mes_zero = divmod(indice_mes, 12)
    mes = mes_zero + 1
    return date(ano, mes, min(hoje.day, monthrange(ano, mes)[1]))


def inicio_periodo_listagem(hoje: date) -> date:
    """Janela de três meses usada por consultas de solicitações, ocorrências e OS."""
    return subtrair_meses(hoje, 3)


def formatar_periodo(inicio: date, fim: date) -> dict[str, str]:
    """Projeta datas de período analítico sem modificar seus limites [início, fim)."""
    return {"inicio": inicio.isoformat(), "fim_exclusivo": fim.isoformat()}
