from typing import Literal
from pydantic import BaseModel, Field, field_validator
from app.core import Emocao
from app.schemas import LIMITE_ID_SESSAO, LIMITE_IMAGENS_POR_MENSAGEM, validar_url_imagem, VisualizacaoPublica

# ConversaEntrada: contrato/estrutura de chat; usado pelos consumidores desta interface.
class ConversaEntrada(BaseModel):
    mensagem: str = Field(
        min_length=1,
        max_length=4000,
    )

    plataforma: Literal["web", "mobile"]

    thread_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=LIMITE_ID_SESSAO,
    )

    imagens: list[str] = Field(
        default_factory=list,
        max_length=LIMITE_IMAGENS_POR_MENSAGEM,
    )

    @field_validator("mensagem", "thread_id", mode="before")
    @classmethod
    def normalizar_texto(cls, valor):
        """Confere texto conforme o contrato deste domínio. Usado pelo fluxo de schemas."""
        if isinstance(valor, str):
            return valor.strip()
        return valor

    @field_validator("imagens")
    @classmethod
    def validar_imagens(cls, imagens: list[str]) -> list[str]:
        """Confere imagens conforme o contrato deste domínio. Usado pelo fluxo de schemas."""
        return [validar_url_imagem(imagem) for imagem in imagens]


# ConversaSaida: contrato/estrutura de chat; usado pelos consumidores desta interface.
class ConversaSaida(BaseModel):
    thread_id: str

    intencao: Literal[
        "ajuda_geral",
        "faq",
        "solicitacao",
        "ocorrencia",
        "evento",
        "analytics",
        "visualizacao",
        "feedback",
        "analista_compras",
        "fora_de_escopo",
    ] | None

    resposta: str
    emocao: Emocao = Emocao.NEUTRO
    confirmacao: Literal["sim", "nao"] = "nao"
    visualizacao: VisualizacaoPublica | None = Field(default=None, exclude_if=lambda v: v is None)
