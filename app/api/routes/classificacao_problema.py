"""Fronteira HTTP da classificação; regras pertencem ao serviço."""

from fastapi import APIRouter
from app.schemas import ClassificarProblemaRequest, ClassificarProblemaResponse
from app.services import classificar_problema_dados

# Preserva prefixo, tag e contrato HTTP já consumidos pelo site/aplicativo.
router = APIRouter(tags=["Observability"], prefix="/classificar")


@router.post("/classificar-problema", response_model=ClassificarProblemaResponse)
async def classificar_problema(classificar_problema: ClassificarProblemaRequest) -> ClassificarProblemaResponse:
    """
    Endpoint para classificar um problema com base no título, descrição e categoria do equipamento.

    Args:
        classificar_problema (ClassificarProblemaRequest): Dados de entrada para classificação do problema.
    """
    # A rota mantém o contrato HTTP; a regra é executada pelo serviço.
    return await classificar_problema_dados(classificar_problema)
