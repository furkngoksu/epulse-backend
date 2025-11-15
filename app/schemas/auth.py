from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    nationalid: str = Field(..., min_length=11, max_length=11)
    password: str

class LoginResponse(BaseModel):
    success: bool = True
    data: dict
