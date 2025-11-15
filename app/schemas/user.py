from pydantic import BaseModel, EmailStr, Field
from datetime import date
from app.models.user import GenderEnum, RoleEnum
from uuid import UUID


class UserCreate(BaseModel):
    nationalId: str = Field(..., min_length=11, max_length=11)
    firstName: str
    lastName: str
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    phoneNumber: str
    dateOfBirth: date
    gender: GenderEnum


class UserResponse(BaseModel):
    id: UUID
    nationalId: str
    firstName: str
    lastName: str
    email: str
    phoneNumber: str
    role: RoleEnum

    class Config:
        from_attributes = True


