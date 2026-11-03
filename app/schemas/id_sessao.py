from typing import Annotated
from fastapi import Path
from pydantic import BeforeValidator

# LIMITE_ID_SESSAO: Limite operacional/contratual usado pela validação e pelo processamento deste módulo.
LIMITE_ID_SESSAO = 100


def normalizar_id_sessao(valor: str) -> str:
    """Remove espaços externos do ID de sessão quando recebido como texto. Usado pelo fluxo de schemas."""
    return valor.strip() if isinstance(valor, str) else valor


# IdSessaoCaminho: Recurso compartilhado de idsessaocaminho usado pelas funções deste módulo e pela interface pública.
IdSessaoCaminho = Annotated[
    str,
    BeforeValidator(normalizar_id_sessao),
    Path(min_length=1, max_length=LIMITE_ID_SESSAO),
]
