# Re-export from centralized repositories and services modules
from app.api.deps.repositories import (
    get_prescription_repository,
    get_prescription_item_repository,
)
from app.api.deps.services import get_prescription_service

__all__ = [
    "get_prescription_repository",
    "get_prescription_item_repository",
    "get_prescription_service",
]
