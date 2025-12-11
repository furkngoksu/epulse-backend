# Re-export from centralized repositories module
from app.api.deps.repositories import get_user_repository

__all__ = ["get_user_repository"]
