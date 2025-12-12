import uuid
from app.repositories.user import UserRepository
from app.schemas.auth import ForgotPasswordRequest, LoginRequest, RefreshTokenRequest, RegisterRequest, RegisterResponse, LoginResponse, ResetPasswordRequest
from app.core.security import create_password_reset_token, decode_password_reset_token, decode_token, hash_password, create_access_token, create_refresh_token, verify_password
from app.exceptions import (
    ConflictException,
    NotFoundException,
    UnauthorizedException
)
from app.schemas.auth import (
    ForgotPasswordRequest, ForgotPasswordResponse,
    LoginRequest, LoginResponse,
    RefreshTokenRequest,
    RegisterRequest, RegisterResponse,
    ResetPasswordRequest, ResetPasswordResponse, UserResponse
)
from app.models.user import UserModel

class AuthService:

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def register(self, request: RegisterRequest) -> RegisterResponse:

        existing_email = self.user_repository.get_by_email(email=request.email)
        if existing_email:
            raise ConflictException("Email already exists")

        existing_tc = self.user_repository.get_by_national_id(national_id=request.national_id)
        if existing_tc:
            raise ConflictException("National ID already registered")

        password_hash = hash_password(request.password)
        user = UserModel(
            national_id=request.national_id,
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            phone_number=request.phone_number,
            password_hash=password_hash,
            date_of_birth=request.date_of_birth,
            gender=request.gender,
        )
        saved_user = self.user_repository.create(user=user)
        access_token = create_access_token({"sub": str(saved_user.id)})
        refresh_token = create_refresh_token({"sub": str(saved_user.id)})


        return RegisterResponse(
            user=UserResponse.model_validate(saved_user),
            access_token=access_token,
            refresh_token=refresh_token   
        )

    def login(self, request: LoginRequest) -> LoginResponse:
        user = self.user_repository.get_by_national_id(national_id=request.national_id)
        if not user:
            raise UnauthorizedException("Invalid national ID or password")

        if not verify_password(request.password, user.password_hash):
            raise UnauthorizedException("Invalid national ID or password")

        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        return LoginResponse(
            success=True,
            user=UserResponse.model_validate(user),
            access_token=access_token,
            refresh_token=refresh_token
        )

    def refresh_token(self, request: RefreshTokenRequest) -> LoginResponse:
        payload = decode_token(request.refresh_token, refresh=True)
        user_id = payload.get("sub")

        user = self.user_repository.get_by_id(uuid.UUID(user_id))
        if not user:
            raise UnauthorizedException("User not found")

        new_access_token = create_access_token({"sub": user_id})
        new_refresh_token = create_refresh_token({"sub": user_id})

        return LoginResponse(
            success=True,
            user=UserResponse.model_validate(user),
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )
    
    def forgot_password(self, request: ForgotPasswordRequest) -> ForgotPasswordResponse:
        
        user = self.user_repository.get_by_email(request.email)
        if not user:
            raise NotFoundException("User not found")
        
        token = create_password_reset_token(str(user.id))

        # TODO: Mail gönderme işlemi burada yapılacak

        return ForgotPasswordResponse(reset_token=token)
    
    def reset_password(self, request: ResetPasswordRequest) -> ResetPasswordResponse:
        
        user_id_str = decode_password_reset_token(request.token)
        user_id = uuid.UUID(user_id_str)

        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise UnauthorizedException("Invalid reset token")

        user.password_hash = hash_password(request.new_password)
        self.user_repository.update(user)

        return ResetPasswordResponse()

