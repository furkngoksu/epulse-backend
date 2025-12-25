from fastapi import APIRouter, Depends, status

from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    RegisterResponse,
    LoginResponse,
)
from app.schemas.password_reset import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    VerifyOTPRequest,
    VerifyOTPResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
)
from app.services import AuthService
from app.api.deps.auth import get_auth_service
from app.schemas.base import SuccessResponse

router = APIRouter()


@router.post(
    "/register",
    response_model=SuccessResponse[RegisterResponse],
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterRequest, auth: AuthService = Depends(get_auth_service)
) -> SuccessResponse[RegisterResponse]:
    response = auth.register(request)
    return SuccessResponse(content=response)


@router.post(
    "/login",
    response_model=SuccessResponse[LoginResponse],
    status_code=status.HTTP_200_OK,
)
def login(
    request: LoginRequest, auth: AuthService = Depends(get_auth_service)
) -> SuccessResponse[LoginResponse]:
    response = auth.login(request)
    return SuccessResponse(content=response)


@router.post(
    "/refresh",
    response_model=SuccessResponse[LoginResponse],
    status_code=status.HTTP_200_OK,
)
def refresh_token(
    request: RefreshTokenRequest, auth: AuthService = Depends(get_auth_service)
) -> SuccessResponse[LoginResponse]:
    response = auth.refresh_token(request)
    return SuccessResponse(content=response)


@router.post(
    "/forgot-password",
    response_model=SuccessResponse[ForgotPasswordResponse],
    status_code=status.HTTP_200_OK,
)
def forgot_password(
    data: ForgotPasswordRequest, auth: AuthService = Depends(get_auth_service)
) -> SuccessResponse[ForgotPasswordResponse]:
    response = auth.forgot_password(data)
    return SuccessResponse(content=response)


@router.post(
    "/verify-otp",
    response_model=SuccessResponse[VerifyOTPResponse],
    status_code=status.HTTP_200_OK,
)
def verify_otp(
    data: VerifyOTPRequest, auth: AuthService = Depends(get_auth_service)
) -> SuccessResponse[VerifyOTPResponse]:
    response = auth.verify_otp(data)
    return SuccessResponse(content=response)


@router.post(
    "/reset-password",
    response_model=SuccessResponse[ResetPasswordResponse],
    status_code=status.HTTP_200_OK,
)
def reset_password(
    data: ResetPasswordRequest, auth: AuthService = Depends(get_auth_service)
) -> SuccessResponse[ResetPasswordResponse]:
    response = auth.reset_password(data)
    return SuccessResponse(content=response)
