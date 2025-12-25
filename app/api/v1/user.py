from uuid import UUID
from fastapi import APIRouter, Depends, status

from app.api.deps.auth import get_current_user
from app.api.deps.services import get_user_service
from app.schemas.base import SuccessResponse
from app.schemas.user import User, UserResponse, UserUpdate
from app.services import UserService

router = APIRouter()


@router.get("/profile", response_model=SuccessResponse[UserResponse], status_code=status.HTTP_200_OK)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
) -> SuccessResponse[UserResponse]:

    user_profile = user_service.get_user_profile(
        current_user_id=current_user.id,
        current_user_role=current_user.role,
        requested_user_id=current_user.id
    )
    return SuccessResponse(content=user_profile)


@router.get("/profile/{user_id}", response_model=SuccessResponse[UserResponse], status_code=status.HTTP_200_OK)
def get_user_profile(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
) -> SuccessResponse[UserResponse]:

    user_profile = user_service.get_user_profile(
        current_user_id=current_user.id,
        current_user_role=current_user.role,
        requested_user_id=user_id
    )
    return SuccessResponse(content=user_profile)


@router.patch("/profile", response_model=SuccessResponse[UserResponse], status_code=status.HTTP_200_OK)
def update_current_user_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
) -> SuccessResponse[UserResponse]:
    
    updated_user = user_service.update_user_profile(
        user_id=current_user.id,
        data=data
    )
    return SuccessResponse(content=updated_user)

