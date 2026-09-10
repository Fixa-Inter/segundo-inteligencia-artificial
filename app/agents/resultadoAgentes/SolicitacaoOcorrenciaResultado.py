from typing import Literal

from pydantic import BaseModel


class SolicitacaoOcorrenciaResultado(BaseModel):
    agente: str
    resposta: str
    status: Literal[
        "SUCESSO",
        "SUCESSO_PARCIAL",
        "AGUARDANDO_INFORMACAO",
        "SEM_RESULTADO",
        "ERRO_VALIDACAO",
        "ERRO_FERRAMENTA",
        "ERRO_MODELO",
        "TIMEOUT",
    ]
