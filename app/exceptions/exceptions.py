from fastapi import HTTPException, status
from typing import Optional

class BadRequestException(HTTPException):
    def __init__(self, message: str, fields: Optional[dict] = None):
        detail: dict[str, object] = {
            "code": "BAD_REQUEST",
            "message": message,
        }
        if fields:
            detail["fields"] = fields

        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

class UnauthorizedException(HTTPException):
    def __init__(self, message: str = "Unauthorized"):
        detail: dict[str, object] = {
            "code": "UNAUTHORIZED",
            "message": message,
        }
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail)

class ForbiddenException(HTTPException):
    def __init__(self, message: str = "Forbidden"):
        detail: dict[str, object] = {
            "code": "FORBIDDEN",
            "message": message,
        }
        super().__init__(status.HTTP_403_FORBIDDEN, detail)

class NotFoundException(HTTPException):
    def __init__(self, message: str = "Not found"):
        detail: dict[str, object] = {
            "code": "NOT_FOUND",
            "message": message,
        }
        super().__init__(status.HTTP_404_NOT_FOUND, detail)

class ConflictException(HTTPException):
    def __init__(self, message: str = "Conflict"):
        detail: dict[str, object] = {
            "code": "CONFLICT",
            "message": message,
        }
        super().__init__(status.HTTP_409_CONFLICT, detail)

class PermissionDeniedException(HTTPException):
    def __init__(self, message: str = "Permission Denied"):
        detail: dict[str, object] = {
            "code": "PERMISSION_DENIED",
            "message": message,
        }
        super().__init__(status.HTTP_403_FORBIDDEN, detail)
