from fastapi import APIRouter, Depends

from app.schemas.auth import LoginRequest, RegisterRequest, RegisterResponse, LoginResponse
from app.services import AuthService
from app.api.deps.auth import get_auth_service

router = APIRouter()

@router.post("/register")
def register(
    request: RegisterRequest, 
    auth: AuthService = Depends(get_auth_service)
) -> RegisterResponse:
    response = auth.register(request)
    return response

@router.post("/login")
def login(
    request: LoginRequest, 
    auth: AuthService = Depends(get_auth_service)
) -> LoginResponse:
    response = auth.login(request)
    return response
