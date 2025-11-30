from pydantic import BaseModel, Field


class DoctorProfileBase(BaseModel):
    hospital_id: int
    specialty: str = Field(..., min_length=1, max_length=100)


class DoctorProfileCreate(DoctorProfileBase):
    user_id: int


class DoctorProfileUpdate(BaseModel):
    hospital_id: int | None = None
    specialty: str | None = Field(None, min_length=1, max_length=100)


class DoctorProfileResponse(DoctorProfileBase):
    id: int

    class Config:
        from_attributes = True


class DoctorProfileDetailResponse(DoctorProfileResponse):
    """Detailed response with user and hospital information"""
    user: dict | None = None
    hospital: dict | None = None

    class Config:
        from_attributes = True
