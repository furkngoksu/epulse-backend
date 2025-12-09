from pydantic import BaseModel
from typing import Optional
from app.models.prescription import Status

class PrescriptionBase(BaseModel):
    notes: Optional[str] = None


class PrescriptionCreate(PrescriptionBase):
    patient_id: str


class PrescriptionUpdate(BaseModel):
    notes: Optional[str] = None
    status: Optional[Status] = None


class Prescription(PrescriptionBase):
    id: str
    doctor_id: str
    patient_id: str
    status: Optional[Status] = None

    class Config:
        from_attributes = True
