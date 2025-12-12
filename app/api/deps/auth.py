from fastapi import Depends, Header
from app.core.security import get_user_id_from_token
from app.repositories.user import UserRepository
from app.exceptions.exceptions import UnauthorizedException, ForbiddenException
from app.schemas.user import User
from app.models.user import RoleEnum
from app.api.deps.user import get_user_repository
from app.services.auth_service import AuthService

def get_current_user(
    user_repo: UserRepository = Depends(get_user_repository),
    authorization: str = Header(None),
) -> User:
    if not authorization:
        raise UnauthorizedException("Authorization header missing")
    
    if not authorization.startswith("Bearer "):
        raise UnauthorizedException("Invalid authorization format")

    token = authorization.split(" ")[1]
    user_id = get_user_id_from_token(token)
    user = user_repo.get_by_id(user_id=user_id)
    
    if not user:
        raise UnauthorizedException("User not found")

    return User.model_validate(user)

def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != RoleEnum.ADMIN:
        raise ForbiddenException("Admin access required")
    return current_user

def get_current_doctor(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != RoleEnum.DOCTOR:
        raise ForbiddenException("Doctor access required")
    return current_user

def get_current_doctor_or_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role not in (RoleEnum.DOCTOR, RoleEnum.ADMIN):
        raise ForbiddenException("Doctor or admin access required")
    return current_user

def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(user_repository=user_repo)