from pydantic import BaseModel
from typing import Optional
import uuid


class PrescriptionItemBase(BaseModel):
    dosage: Optional[str] = None
    duration: Optional[int] = None


class PrescriptionItemCreate(PrescriptionItemBase):
    prescription_id: uuid.UUID
    medication_id: uuid.UUID


class PrescriptionItemUpdate(BaseModel):
    dosage: Optional[str] = None
    duration: Optional[int] = None


class PrescriptionItem(PrescriptionItemBase):
    id: uuid.UUID
    prescription_id: uuid.UUID
    medication_id: uuid.UUID

    class Config:
        from_attributes = True
