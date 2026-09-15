from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CriarSolicitacaoRequest(BaseModel):
    """Dados da solicitação preenchidos pela IA, base para o args_schema da tool.

    A tool obtém usuario_id de context['usuario']; o serviço o acrescenta ao
    JSON enviado à API. Identidade e credenciais não são argumentos da IA.
    A existência dos IDs e a autorização devem ser verificadas pela API.
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
