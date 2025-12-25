import logging
from uuid import UUID
from app.repositories.user import UserRepository
from app.schemas.user import UserResponse, UserUpdate
from app.models.user import RoleEnum
from app.exceptions import NotFoundException, ConflictException, ForbiddenException

logger = logging.getLogger(__name__)

class UserService:

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def get_user_by_id(self, user_id: UUID) -> UserResponse:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        return UserResponse.model_validate(user)

    def get_user_profile(self, current_user_id: UUID, current_user_role: RoleEnum, requested_user_id: UUID) -> UserResponse:

        # Authorization check
        if current_user_role != RoleEnum.admin:
            if current_user_id != requested_user_id:
                raise ForbiddenException("You can only access your own profile")

        # Fetch the requested user
        user = self.user_repo.get_by_id(requested_user_id)
        if not user:
            raise NotFoundException("User not found")

        return UserResponse.model_validate(user)

    def get_users(self, skip=0, limit=100):
        users = self.user_repo.get_users(skip, limit)
        return [UserResponse.model_validate(u) for u in users]

    def update_user_profile(self, user_id: UUID, data: UserUpdate) -> UserResponse:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        if data.email and data.email != user.email:
            if self.user_repo.get_by_email(data.email):
                raise ConflictException("Email already taken")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)

        updated = self.user_repo.update(user)
        logger.info("User profile updated successfully", extra={"user_id": str(user_id)})
        return UserResponse.model_validate(updated)
    
    def get_total_user_count(self) -> int:
        return self.user_repo.get_total_count()