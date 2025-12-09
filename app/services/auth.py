from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, RegisterResponse, LoginResponse
from app.core.security import hash_password, create_access_token, create_refresh_token, verify_password
from app.exceptions.exceptions import (
    ConflictException,
    UnauthorizedException
)
from app.models.user import UserModel
from app.schemas.user import UserResponse

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
