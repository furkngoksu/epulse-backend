import uuid
from pydantic import BaseModel, Field
from app.schemas.user import UserResponse
from app.schemas.doctor_profile import DoctorProfileResponse
from pydantic.networks import EmailStr
from datetime import date

class LoginRequest(BaseModel):
    national_id: str = Field(..., min_length=11, max_length=11)
    password: str


class LoginResponse(BaseModel):
    success: bool = True
    user: UserResponse
    access_token: str
    refresh_token: str


class RegisterResponse(BaseModel):
    user: UserResponse
    access_token: str
    refresh_token: str


class RegisterRequest(BaseModel):
    national_id: str = Field(..., min_length=11, max_length=11)
    first_name: str
    last_name: str
    email: str
    phone_number: str
    password: str
    date_of_birth: date
    gender: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    reset_token: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class ResetPasswordResponse(BaseModel):
    pass


class RegisterDoctorRequest(BaseModel):
    # User fields
    national_id: str = Field(..., min_length=11, max_length=11)
    first_name: str
    last_name: str
    email: str
    phone_number: str
    password: str
    date_of_birth: str
    gender: str

    # Doctor profile fields
    clinic_id: uuid.UUID
    specialty: str = Field(..., min_length=1, max_length=100)


class RegisterDoctorResponse(BaseModel):
    user: UserResponse
    doctor_profile: DoctorProfileResponse
    access_token: str
    refresh_token: str
