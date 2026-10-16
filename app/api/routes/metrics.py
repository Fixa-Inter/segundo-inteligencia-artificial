from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST

from app.observability.metricas import gerar_conteudo_prometheus


router = APIRouter(tags=["Observability"])


@router.get("/metrics", include_in_schema=False)
async def metrics() -> Response:
    return Response(
        content=gerar_conteudo_prometheus(),
        media_type=CONTENT_TYPE_LATEST,
    )
