import uuid
from pydantic import BaseModel, Field


class ClinicBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    hospital_id: uuid.UUID


class ClinicCreate(ClinicBase):
    pass


class ClinicUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    hospital_id: uuid.UUID | None = None


class ClinicResponse(ClinicBase):
    id: uuid.UUID

    class Config:
        from_attributes = True
