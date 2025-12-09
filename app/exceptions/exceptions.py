from fastapi import HTTPException, status

class BadRequestException(HTTPException):
    def __init__(self, message: str, fields: dict | None = None):
        detail = {
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
        detail = {
            "code": "UNAUTHORIZED",
            "message": message,
        }
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )

class ForbiddenException(HTTPException):
    def __init__(self, message: str = "Forbidden"):
        detail = {
            "code": "FORBIDDEN",
            "message": message,
        }
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

class NotFoundException(HTTPException):
    def __init__(self, message: str = "Not found"):
        detail = {
            "code": "NOT_FOUND",
            "message": message,
        }
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class ConflictException(HTTPException):
    def __init__(self, message: str = "Conflict"):
        detail = {
            "code": "CONFLICT",
            "message": message,
        }
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )

class PermissionDeniedException(HTTPException):
    def __init__(self, message: str = "Permission Denied"):
        detail = {
            "code": "PERMISSION_DENIED",
            "message": message,
        }
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )
