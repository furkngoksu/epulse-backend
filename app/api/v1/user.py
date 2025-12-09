from fastapi import APIRouter, Depends

from app.api.deps.auth import get_current_user
from app.schemas.user import User

router = APIRouter()

@router.get("/profile")
def get_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user's profile.
    Requires authentication via Bearer token.
    """
    return {
        "success": True,
        "data": {
            "first_name": current_user.first_name,
            "last_name": current_user.last_name
        }
    }
