from fastapi import APIRouter, status
from app.schemas import HealthResponse

# router: Roteador HTTP que registra endpoints e contratos deste módulo.
router = APIRouter(tags=["Health"])


# Devolve status ok e nome do serviço, sem verificar dependências externas. Usado pelo fluxo de routes.
@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="segundo-inteligencia-artificial",
    )
