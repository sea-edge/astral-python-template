from __future__ import annotations

from fastapi import APIRouter

from app.slices.health.routes import router as health_router
from app.slices.users.routes import router as users_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(users_router)
