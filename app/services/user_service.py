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
        """
        Get user profile with authorization checks.
        - Admin users can access any profile
        - Non-admin users (doctor/patient) can only access their own profile
        """
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

    def update_user_profile(self, user_id: UUID, data: UserUpdate):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        restricted = ["national_id", "date_of_birth"]
        for field in restricted:
            if getattr(data, field, None) is not None:
                raise ForbiddenException(f"{field} cannot be updated")

        if data.email and data.email != user.email:
            if self.user_repo.get_by_email(data.email):
                raise ConflictException("Email already taken")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)

        updated = self.user_repo.update(user)
        logger.info("User profile updated successfully", extra={"user_id": str(user_id)})
        return UserResponse.model_validate(updated)

    def update_profile_photo(self, user_id: UUID, url: str):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        user.profile_photo_url = url
        updated = self.user_repo.update(user)
        return UserResponse.model_validate(updated)

    def admin_update_user(self, admin_id: UUID, user_id: UUID, data: UserUpdate):
        admin = self.user_repo.get_by_id(admin_id)
        if not admin or admin.role != RoleEnum.admin:
            raise ForbiddenException("Only admin can modify these fields")

        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)

        updated = self.user_repo.update(user)
        return UserResponse.model_validate(updated)
    
    def get_total_user_count(self) -> int:
        return self.user_repo.get_total_count()
    
    def get_user_counts_by_role(self) -> dict[str, int]:
        total_users = self.user_repo.get_total_count()
        total_admins = self.user_repo.get_count_by_role(RoleEnum.admin)
        total_doctors = self.user_repo.get_count_by_role(RoleEnum.doctor)
        total_patients = self.user_repo.get_count_by_role(RoleEnum.patient)
        
        return {
            "total_users": total_users,
            "total_admins": total_admins,
            "total_doctors": total_doctors,
            "total_patients": total_patients
        }
