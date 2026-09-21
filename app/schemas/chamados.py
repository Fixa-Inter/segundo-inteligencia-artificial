from pydantic import Field

from app.tools.toolsRequest.CriarSolicitacaoRequest import (
    CriarSolicitacaoRequest,
)


class CriarChamadoRequest(CriarSolicitacaoRequest):
    imagens: list[str] = Field(
        min_length=1,
        description=(
            "Lista com pelo menos uma URL de imagem do problema."
        ),
    )