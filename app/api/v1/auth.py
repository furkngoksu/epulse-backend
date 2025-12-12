from fastapi import APIRouter, Depends

from app.schemas.auth import ForgotPasswordRequest, ForgotPasswordResponse, ForgotPasswordResponse, LoginRequest, RefreshTokenRequest, RegisterRequest, RegisterResponse, LoginResponse, ResetPasswordRequest, ResetPasswordResponse, ResetPasswordResponse
from app.services import AuthService
from app.api.deps.auth import get_auth_service
from app.schemas.base import SuccessResponse

router = APIRouter()

@router.post("/register", response_model=SuccessResponse[RegisterResponse])
def register(request: RegisterRequest, auth: AuthService = Depends(get_auth_service)) -> SuccessResponse[RegisterResponse]:
    response = auth.register(request)
    return SuccessResponse(content=response)

@router.post("/login", response_model=SuccessResponse[LoginResponse])
def login(
    request: LoginRequest, 
    auth: AuthService = Depends(get_auth_service)
) -> SuccessResponse[LoginResponse]:
    response = auth.login(request)
    return SuccessResponse(content=response)

@router.post("/refresh", response_model=SuccessResponse[LoginResponse])
def refresh_token(
    request: RefreshTokenRequest,
    auth: AuthService = Depends(get_auth_service)
) -> SuccessResponse[LoginResponse]:
    response = auth.refresh_token(request)
    return SuccessResponse(content=response)

@router.post("/forgot-password", response_model=SuccessResponse[ForgotPasswordResponse])
def forgot_password(
    request: ForgotPasswordRequest,
    auth: AuthService = Depends(get_auth_service)
) -> SuccessResponse[ForgotPasswordResponse]:
    response = auth.forgot_password(request)
    return SuccessResponse(content=response)

@router.post("/reset-password", response_model=SuccessResponse[ResetPasswordResponse])
def reset_password(
    request: ResetPasswordRequest,
    auth: AuthService = Depends(get_auth_service)
) -> SuccessResponse[ResetPasswordResponse]:
    response = auth.reset_password(request)
    return SuccessResponse(content=response)