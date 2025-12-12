import uuid
from pydantic import BaseModel, Field


class DoctorProfileBase(BaseModel):
    hospital_id: uuid.UUID
    specialty: str = Field(..., min_length=1, max_length=100)


class DoctorProfileCreate(DoctorProfileBase):
    user_id: uuid.UUID


class DoctorProfileUpdate(BaseModel):
    hospital_id: uuid.UUID | None = None
    specialty: str | None = Field(None, min_length=1, max_length=100)


class DoctorProfileResponse(DoctorProfileBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


class DoctorProfileDetailResponse(DoctorProfileResponse):
    """Detailed response with user and hospital information"""
    user: dict | None = None
    hospital: dict | None = None

    class Config:
        from_attributes = True
