from fastapi import APIRouter

from app.api.routes.analytics import router as analytics_router
from app.api.routes.auth import router as auth_router
from app.api.routes.chat import router as chat_router
from app.api.routes.chamados import router as chamados_router
from app.api.routes.health import router as health_router
from app.api.routes.ordens_servico import router as ordens_router


api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(chat_router)
api_router.include_router(chamados_router)
api_router.include_router(ordens_router)
api_router.include_router(analytics_router)