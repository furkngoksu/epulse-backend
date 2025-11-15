from fastapi import APIRouter

from app.api.v1.auth import router as auth_router

app_router = APIRouter(prefix="/api/v1")

app_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])