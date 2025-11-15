from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.api.deps.db import get_db
from app.core.security import get_user_id_from_token
from app.repositories.user import UserRepository
from app.exceptions.exceptions import UnauthorizedException

def get_current_user(
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    if not authorization:
        raise UnauthorizedException("Authorization header missing")

    if not authorization.startswith("Bearer "):
        raise UnauthorizedException("Invalid authorization format")

    token = authorization.split(" ")[1]

    user_id = get_user_id_from_token(token)
    user = UserRepository.get_by_id(db, user_id)

    if not user:
        raise UnauthorizedException("User not found")

    return user
