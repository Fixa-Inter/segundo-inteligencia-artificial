from pydantic import BaseModel, ConfigDict, Field


class CriarOcorrenciaRequest(BaseModel):
    """Argumentos da IA; identidade e ID do equipamento são resolvidos pelo código."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    local_endereco_id: int = Field(
        strict=True, gt=0,
        description="ID do local retornado por buscar_opcoes_ocorrencia e confirmado pelo usuário.",
    )
    categoria_problema_id: int = Field(
        strict=True, ge=1, le=10,
        description="ID de 1 a 10 conforme o mapeamento de categorias do prompt, confirmado pelo usuário.",
    )
    titulo: str = Field(min_length=1, description="Título proposto com base no relato e confirmado pelo usuário.")
    descricao_ocorrencia: str = Field(min_length=1, description="Descrição curta e fiel ao relato, confirmada pelo usuário.")
    descricao_local: str = Field(min_length=1, description="Detalhes fornecidos pelo usuário sobre onde a manutenção ocorreu. Não inventar.")
    prioridade: int = Field(strict=True, ge=0, le=2, description="Prioridade confirmada: alta=0, média=1, baixa=2.")
    equipamento_codigo: str | None = Field(
        default=None, min_length=1,
        description="Código exato informado pelo usuário e validado na busca. Null somente quando não houver equipamento indicado.",
    )
