import uuid
from pydantic import BaseModel, Field

class ForgotPasswordRequest(BaseModel):
    email: str


class ForgotPasswordResponse(BaseModel):
    success: bool = True
    request_id: uuid.UUID
    message: str = "If the email exists, an OTP code has been sent"


class VerifyOTPRequest(BaseModel):
    request_id: uuid.UUID
    otp: str = Field(..., min_length=6, max_length=6, pattern="^[0-9]{6}$")


class VerifyOTPResponse(BaseModel):
    success: bool = True
    reset_token: str
    message: str = "OTP verified successfully"


class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: str = Field(..., min_length=8)


class ResetPasswordResponse(BaseModel):
    success: bool = True
    message: str = "Password reset successfully"
