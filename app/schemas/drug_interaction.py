from pydantic import BaseModel
from app.models.drug_interaction import SeverityEnum


class DrugInteractionBase(BaseModel):
    medication_id_1: int
    medication_id_2: int
    severity: SeverityEnum
    interaction_description: str | None = None


class DrugInteractionCreate(DrugInteractionBase):
    pass


class DrugInteractionUpdate(BaseModel):
    medication_id_1: int | None = None
    medication_id_2: int | None = None
    severity: SeverityEnum | None = None
    interaction_description: str | None = None


class DrugInteractionResponse(DrugInteractionBase):
    id: int

    class Config:
        from_attributes = True
