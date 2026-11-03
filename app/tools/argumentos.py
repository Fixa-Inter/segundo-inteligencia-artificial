"""Validação compartilhada da fronteira entre argumentos do modelo e ToolRuntime."""

from langchain.tools import ToolRuntime
from pydantic import BaseModel, model_validator

class ArgumentosComRuntime(BaseModel):
    """Remove somente o ToolRuntime Python injetado pelo SDK nos schemas de tools.

    Um dicionário enviado pelo modelo com a chave runtime não é um contexto
    autenticado e permanece sujeito à rejeição de campos extras do contrato.
    A classe não altera as configurações Pydantic dos schemas filhos.
    """

    @model_validator(mode="before")
    @classmethod
    def separar_runtime_injetado(cls, dados):
        """Preserva argumentos JSON e separa somente o objeto confiável do SDK."""
        if isinstance(dados, dict) and isinstance(dados.get("runtime"), ToolRuntime):
            return {chave: valor for chave, valor in dados.items() if chave != "runtime"}
        return dados
