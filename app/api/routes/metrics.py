from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST
from app.observability import gerar_conteudo_prometheus

# router: Roteador HTTP que registra endpoints e contratos deste módulo.
router = APIRouter(tags=["Observability"])


# Devolve as métricas agregadas no formato Prometheus. Usado pelo fluxo de routes.
@router.get("/metrics", include_in_schema=False)
async def metrics() -> Response:
    return Response(
        content=gerar_conteudo_prometheus(),
        media_type=CONTENT_TYPE_LATEST,
    )
