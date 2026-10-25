from fastapi import APIRouter

from app.api.routes.chat import router as chat_router
from app.api.routes.metrics import router as metrics_router
from app.api.routes.health import router as health_router
from app.api.routes.classificacao_problema import router as classificacao_problema_router
from app.api.routes.sessoes import router as sessoes_router


api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(chat_router)
api_router.include_router(metrics_router)
api_router.include_router(classificacao_problema_router)
api_router.include_router(sessoes_router)
