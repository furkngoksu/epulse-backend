from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
from app.exceptions.exceptions import UnauthorizedException
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_REFRESH_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_token(token: str, refresh: bool = False) -> dict:
    try:
        secret = settings.JWT_REFRESH_SECRET_KEY if refresh else settings.JWT_SECRET_KEY

        payload = jwt.decode(token, secret, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise UnauthorizedException("Invalid or expired token.")


def get_user_id_from_token(token: str) -> uuid.UUID:
    payload = decode_token(token)
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException("Token does not contain user ID.")
    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise UnauthorizedException("Invalid user ID in token.")

    return user_id


def create_password_reset_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=1)

    to_encode = {
        "sub": user_id,
        "type": "password_reset",
        "exp": int(expire.timestamp()),
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_password_reset_token(token: str) -> str:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != "password_reset":
            raise UnauthorizedException("Invalid reset token.")

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise UnauthorizedException("Invalid reset token.")

        return user_id_str

    except JWTError:
        raise UnauthorizedException("Invalid or expired reset token.")
