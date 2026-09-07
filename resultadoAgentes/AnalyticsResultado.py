from typing import Literal

from pydantic import BaseModel

# SUCESSO: tarefa concluída corretamente.
# SUCESSO_PARCIAL: parte da tarefa foi concluída.
# AGUARDANDO_INFORMACAO: faltam informações do usuário.
# SEM_RESULTADO: execução válida, mas não encontrou dados.
# ERRO_VALIDACAO: entrada ou saída incompatível com as regras.
# ERRO_FERRAMENTA: falha ao executar uma tool ou API.
# ERRO_MODELO: falha na chamada ou geração do modelo.
# TIMEOUT: execução excedeu o tempo permitido.
class AnalyticsResultado(BaseModel):
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
