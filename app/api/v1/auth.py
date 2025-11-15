from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps.db import get_db
from app.schemas.auth import LoginRequest
from app.schemas.user import UserCreate, UserResponse
from app.services.user import UserService

router = APIRouter()

@router.post("/register")
def register(data: UserCreate, db: Session = Depends(get_db)):
    user, access_token, refresh_token = UserService.register(db, data)

    return {
        "success": True,
        "data": {
            "user": UserResponse.from_orm(user),
            "token": access_token,
            "refreshToken": refresh_token
        }
    }

@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user, access, refresh = UserService.login(db, req)

    return {
        "success": True,
        "data": {
            "user": {
                "id": user.id,
                "tcKimlikNo": user.nationalId,
                "firstName": user.firstName,
                "lastName": user.lastName,
                "email": user.email,
                "phoneNumber": user.phoneNumber,
                "role": user.role
            },
            "token": access,
            "refreshToken": refresh
        }
    }
