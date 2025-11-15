from sqlalchemy.orm import Session
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest
from app.schemas.user import UserCreate
from app.models.user import User
from app.core.security import hash_password, create_access_token, create_refresh_token, verify_password
from app.exceptions.exceptions import (
    ConflictException,
    UnauthorizedException
)

class UserService:

    @staticmethod
    def register(db: Session, data: UserCreate):

        existing_email = UserRepository.get_by_email(db, data.email)
        if existing_email:
            raise ConflictException("Email already exists")

        existing_tc = UserRepository.get_by_tc(db, data.nationalId)
        if existing_tc:
            raise ConflictException("National ID already registered")

        password_hash = hash_password(data.password)
        user = User(
            nationalId=data.nationalId,
            firstName=data.firstName,
            lastName=data.lastName,
            email=data.email,
            phoneNumber=data.phoneNumber,
            passwordHash=password_hash,
            dateOfBirth=data.dateOfBirth,
            gender=data.gender,
        )
        saved_user = UserRepository.create(db, user)
        access_token = create_access_token({"sub": str(saved_user.id)})
        refresh_token = create_refresh_token({"sub": str(saved_user.id)})

        return saved_user, access_token, refresh_token
    
    @staticmethod
    def login(db: Session, req: LoginRequest):
        user = UserRepository.get_by_tc(db, req.nationalid)
        if not user:
            raise UnauthorizedException("Invalid national ID or password")

        if not verify_password(req.password, user.passwordHash):
            raise UnauthorizedException("Invalid national ID or password")

        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        return user, access_token, refresh_token
