import uuid
from datetime import date
from pydantic import BaseModel, EmailStr
from app.models.user import GenderEnum, RoleEnum

class User(BaseModel):
    id : uuid.UUID
    national_id: str
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    date_of_birth: date
    gender: GenderEnum
    role: RoleEnum

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    phone_number: str | None = None

class UserResponse(User):
    pass
