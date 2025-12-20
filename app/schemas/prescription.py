import uuid
from pydantic import BaseModel
from typing import Optional
from app.models.prescription import Status

class PrescriptionBase(BaseModel):
    notes: Optional[str] = None

class PrescriptionCreate(PrescriptionBase):
    patient_id: uuid.UUID

class PrescriptionUpdate(BaseModel):
    notes: Optional[str] = None
    status: Optional[Status] = None

class Prescription(PrescriptionBase):
    id: uuid.UUID
    doctor_id: uuid.UUID
    patient_id: uuid.UUID
    status: Optional[Status] = None

    class Config:
        from_attributes = True
