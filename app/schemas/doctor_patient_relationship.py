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
