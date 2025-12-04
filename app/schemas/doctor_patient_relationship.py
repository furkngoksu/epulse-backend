from pydantic import BaseModel


class DoctorPatientRelationshipBase(BaseModel):
    doctor_id: int
    patient_id: int


class DoctorPatientRelationshipCreate(DoctorPatientRelationshipBase):
    pass


class DoctorPatientRelationshipResponse(DoctorPatientRelationshipBase):
    id: int

    class Config:
        from_attributes = True
