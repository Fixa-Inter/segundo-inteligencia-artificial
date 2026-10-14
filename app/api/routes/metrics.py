from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST

from app.observability.metrics import prometheus_payload


router = APIRouter(tags=["Observability"])


@router.get("/metrics", include_in_schema=False)
async def metrics() -> Response:
    return Response(
        content=prometheus_payload(),
        media_type=CONTENT_TYPE_LATEST,
    )
