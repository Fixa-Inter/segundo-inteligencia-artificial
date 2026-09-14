from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CriarSolicitacaoRequest(BaseModel):
    """Dados completos para criação, montados pela tool antes de chamar a API.

    Não usar diretamente como args_schema exposto ao modelo: usuario_id deve
    ser inserido pelo código a partir do RuntimeContext autenticado.
    A existência dos IDs e a autorização devem ser verificadas pelo serviço.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    categoria_equipamento_id: int = Field(
        gt=0,
        strict=True,
        description=(
            "ID da categoria do equipamento obtido após consultar o cadastro pela descrição informada pelo usuário. Não inventar IDs; esclarecer ambiguidades."
        ),
    )

    local_endereco_id: int = Field(
        gt=0,
        strict=True,
        description=(
            "ID do local obtido após consultar o cadastro e conferir a correspondência com o local descrito pelo usuário. Esclarecer se houver múltiplos locais possíveis."
        ),
    )

    categoria_problema: int = Field(
        strict=True,
        description=(
            "Código numérico da categoria de problema correspondente ao relato, conforme o mapeamento definido no prompt e aceito pela API. Os códigos permitidos ainda precisam ser definidos para restringir este campo."
        ),
    )

    titulo: str = Field(
        min_length=1,
        description="Resumo do problema em no máximo 10 palavras, sem inventar informações.",
    )

    descricao_problema: str = Field(
        min_length=1,
        description="Resumo detalhado do problema baseado apenas nas informações do usuário.",
    )

    descricao_local: str | None = Field(
        default=None,
        min_length=1,
        description=(
            "Peculiaridades do local explicitamente citadas pelo usuário, como pontos de referência. Usar null quando não houver detalhes adicionais."
        ),
    )

    status: Literal["PENDENTE"] = Field(
        default="PENDENTE",
        description="Estado inicial da solicitação na criação.",
    )
