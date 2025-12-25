import uuid
from pydantic import BaseModel


class DoctorPatientRelationshipBase(BaseModel):
    doctor_id: uuid.UUID
    patient_id: uuid.UUID


class DoctorPatientRelationshipCreate(DoctorPatientRelationshipBase):
    pass


class DoctorPatientRelationshipResponse(DoctorPatientRelationshipBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


class PatientSummary(BaseModel):
    """Patient summary with basic information for doctor's patient list"""

    patient_id: uuid.UUID
    first_name: str
    last_name: str
    age: int
    active_prescriptions: int
    adherence_rate: float

    class Config:
        from_attributes = True
