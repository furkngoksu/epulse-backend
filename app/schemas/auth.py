from pydantic import BaseModel, Field
from app.schemas.user import UserResponse
from pydantic.networks import EmailStr

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
    date_of_birth: str
    gender: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
