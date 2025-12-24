from typing import Optional

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):

    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_ASSISTANT_ID: Optional[str] = None

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
