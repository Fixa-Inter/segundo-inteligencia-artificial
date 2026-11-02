from typing import Literal

from pydantic import BaseModel


class SolicitacaoOcorrenciaResultado(BaseModel):
    agente: str
    resposta: str
    status: Literal[
        "OPERACAO_PREPARADA",
        "SUCESSO",
        "SUCESSO_PARCIAL",
        "AGUARDANDO_INFORMACAO",
        "SEM_RESULTADO",
        "FERRAMENTA_INDISPONIVEL",
        "ERRO_VALIDACAO",
        "ERRO_FERRAMENTA",
        "ERRO_MODELO",
        "TIMEOUT",
    ]
