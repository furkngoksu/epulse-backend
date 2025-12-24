import uuid
from pydantic import BaseModel, Field


class MedicationAliasCreate(BaseModel):
    medication_id: uuid.UUID
    alias_name: str = Field(..., min_length=1, max_length=100)


class MedicationAliasResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    medication_id: uuid.UUID
    alias_name: str

    class Config:
        from_attributes = True
