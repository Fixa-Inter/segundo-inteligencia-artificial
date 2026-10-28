from typing import Annotated

from fastapi import Path
from pydantic import BeforeValidator


LIMITE_ID_SESSAO = 100


def normalizar_id_sessao(valor: str) -> str:
    return valor.strip() if isinstance(valor, str) else valor


IdSessaoCaminho = Annotated[
    str,
    BeforeValidator(normalizar_id_sessao),
    Path(min_length=1, max_length=LIMITE_ID_SESSAO),
]
