from uuid import UUID
from fastapi import APIRouter, Depends

from app.api.deps.auth import get_current_user
from app.api.deps.services import get_user_service
from app.schemas.user import User
from app.services import UserService

router = APIRouter()

@router.get("/profile")
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    Get current authenticated user's profile.

    Returns the profile of the currently logged-in user.

    Returns:
    - id, first_name, last_name, national_id, email, phone_number, date_of_birth, gender, role

    Requires authentication via Bearer token.
    """
    user_profile = user_service.get_user_profile(
        current_user_id=current_user.id,
        current_user_role=current_user.role,
        requested_user_id=current_user.id
    )

    return {
        "success": True,
        "data": {
            "id": user_profile.id,
            "first_name": user_profile.first_name,
            "last_name": user_profile.last_name,
            "national_id": user_profile.national_id,
            "email": user_profile.email,
            "phone_number": user_profile.phone_number,
            "date_of_birth": user_profile.date_of_birth,
            "gender": user_profile.gender,
            "role": user_profile.role
        }
    }

@router.get("/profile/{user_id}")
def get_user_profile(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    Get user profile by ID.

    Authorization:
    - Admin users can access any user's profile
    - Non-admin users (doctor/patient) can only access their own profile

    Returns:
    - id, first_name, last_name, national_id, email, phone_number, date_of_birth, gender, role

    Requires authentication via Bearer token.
    """
    user_profile = user_service.get_user_profile(
        current_user_id=current_user.id,
        current_user_role=current_user.role,
        requested_user_id=user_id
    )

    return {
        "success": True,
        "data": {
            "id": user_profile.id,
            "first_name": user_profile.first_name,
            "last_name": user_profile.last_name,
            "national_id": user_profile.national_id,
            "email": user_profile.email,
            "phone_number": user_profile.phone_number,
            "date_of_birth": user_profile.date_of_birth,
            "gender": user_profile.gender,
            "role": user_profile.role
        }
    }
