from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

CategoriaProblema = Literal[
    "ELETRICA", "HIDRAULICA", "MECANICA", "INFORMATICA", "MOBILIARIO",
    "CLIMATIZACAO", "REDE_CONECTIVIDADE", "SEGURANCA", "ILUMINACAO", "LIMPEZA_CONSERVACAO",
]
Prioridade = Literal["ALTA", "MEDIA", "BAIXA"]


class CriarOcorrenciaEntrada(BaseModel):
    """Dados da proposta; nomes dos enums seguem docs/enum e o Swagger."""
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    local_endereco_id: int = Field(strict=True, gt=0, description="ID do local consultado no Qdrant.")
    categoria_equipamento_id: int = Field(strict=True, gt=0, description="ID da categoria consultada no Qdrant.")
    categoria_problema_id: CategoriaProblema
    prioridade: Prioridade
    titulo: str = Field(min_length=1, max_length=100)
    descricao_ocorrencia: str = Field(min_length=1, max_length=255)
    descricao_local: str = Field(min_length=1, max_length=255)
