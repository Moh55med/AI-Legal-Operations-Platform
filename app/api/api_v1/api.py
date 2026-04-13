"""FastAPI API v1 router and route aggregation"""

from fastapi import APIRouter
from app.api.api_v1.endpoints import cases, documents, deadlines, notifications

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(cases.router, prefix="/cases", tags=["cases"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(deadlines.router, prefix="/deadlines", tags=["deadlines"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
