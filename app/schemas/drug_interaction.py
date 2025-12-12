import uuid
from pydantic import BaseModel
from app.models.drug_interaction import SeverityEnum


class DrugInteractionBase(BaseModel):
    medication_id_1: uuid.UUID
    medication_id_2: uuid.UUID
    severity: SeverityEnum
    interaction_description: str | None = None


class DrugInteractionCreate(DrugInteractionBase):
    pass


class DrugInteractionUpdate(BaseModel):
    medication_id_1: uuid.UUID | None = None
    medication_id_2: uuid.UUID | None = None
    severity: SeverityEnum | None = None
    interaction_description: str | None = None


class DrugInteractionResponse(DrugInteractionBase):
    id: uuid.UUID

    class Config:
        from_attributes = True
