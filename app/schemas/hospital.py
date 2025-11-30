from pydantic import BaseModel, Field


class HospitalBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    address: str = Field(..., min_length=1, max_length=255)
    city: str = Field(..., min_length=1, max_length=50)
    district: str = Field(..., min_length=1, max_length=50)
    phone: str = Field(..., min_length=1, max_length=20)


class HospitalCreate(HospitalBase):
    pass


class HospitalUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    address: str | None = Field(None, min_length=1, max_length=255)
    city: str | None = Field(None, min_length=1, max_length=50)
    district: str | None = Field(None, min_length=1, max_length=50)
    phone: str | None = Field(None, min_length=1, max_length=20)


class HospitalResponse(HospitalBase):
    id: int

    class Config:
        from_attributes = True
