from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.user import router as user_router
from app.api.v1.hospital import router as hospital_router
from app.api.v1.doctor_profile import router as doctor_profile_router

app_router = APIRouter(prefix="/api/v1")

app_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app_router.include_router(user_router, prefix="/user", tags=["User"])
app_router.include_router(hospital_router, prefix="/hospitals", tags=["Hospitals"])
app_router.include_router(doctor_profile_router, prefix="/doctor-profiles", tags=["Doctor Profiles"])