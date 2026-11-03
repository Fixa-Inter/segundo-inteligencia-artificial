from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from app.schemas import ReferenciaVisualizacao, StatusVisualizacao

class VisualizacaoResultado(BaseModel):
    """Texto e uma referência à consulta; não é o payload público do gráfico."""

    model_config = ConfigDict(extra="forbid")

    agente: Literal["visualizacao"]
    resposta: str = Field(min_length=1)
    status: StatusVisualizacao
    visualizacao: ReferenciaVisualizacao | None = None

    @field_validator("resposta")
    @classmethod
    def validar_texto(cls, valor):
        """Confere texto conforme o contrato deste domínio. Usado pelo fluxo de resultados_agentes."""
        if not valor.strip():
            raise ValueError("A resposta deve conter texto legível.")
        return valor

    @model_validator(mode="after")
    def validar_selecao(self):
        """Confere ID selecionado, unidade, atividade e descrição na coleção de cadastro. Usado pelo fluxo de resultados_agentes."""
        sucesso = self.status in {"SUCESSO", "SUCESSO_PARCIAL"}
        if sucesso != (self.visualizacao is not None):
            raise ValueError("Sucesso exige uma referência; demais status não selecionam visualização.")
        return self
