from pydantic import BaseModel, Field
from uuid import UUID


class DoctorProfileBase(BaseModel):
    hospital_id: UUID
    specialty: str = Field(..., min_length=1, max_length=100)


class DoctorProfileCreate(DoctorProfileBase):
    user_id: UUID


class DoctorProfileUpdate(BaseModel):
    hospital_id: UUID | None = None
    specialty: str | None = Field(None, min_length=1, max_length=100)


class DoctorProfileResponse(DoctorProfileBase):
    id: UUID

    class Config:
        from_attributes = True


class DoctorProfileDetailResponse(DoctorProfileResponse):
    """Detailed response with user and hospital information"""
    user: dict | None = None
    hospital: dict | None = None

    class Config:
        from_attributes = True
