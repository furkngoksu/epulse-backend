from pydantic import BaseModel, Field
import uuid


class MedicationBase(BaseModel):
    commercial_name: str = Field(..., min_length=1, max_length=200)
    active_ingredients: str = Field(..., min_length=1, max_length=500)
    dosage_form: str = Field(..., min_length=1, max_length=100)
    strength: str = Field(..., min_length=1, max_length=50)
    manufacturer: str = Field(..., min_length=1, max_length=200)
    description: str | None = None


class MedicationCreate(MedicationBase):
    pass


class MedicationUpdate(BaseModel):
    commercial_name: str | None = Field(None, min_length=1, max_length=200)
    active_ingredients: str | None = Field(None, min_length=1, max_length=500)
    dosage_form: str | None = Field(None, min_length=1, max_length=100)
    strength: str | None = Field(None, min_length=1, max_length=50)
    manufacturer: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None


class MedicationResponse(MedicationBase):
    id: uuid.UUID

    class Config:
        from_attributes = True
