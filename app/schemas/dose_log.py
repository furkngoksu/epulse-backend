from pydantic import BaseModel
from datetime import datetime
from app.models.dose_log import DoseStatusEnum

class DoseLogBase(BaseModel):
    patient_medication_id: str
    scheduled_time: datetime
    taken_time: datetime | None = None
    status : DoseStatusEnum
    notes: str | None = None
    skip_reason: str | None = None

class DoseLogCreate(DoseLogBase):
    pass

class DoseLogUpdate(BaseModel):
    scheduled_time: datetime | None = None
    taken_time: datetime | None = None
    status : DoseStatusEnum | None = None
    notes: str | None = None
    skip_reason: str | None = None

class DoseLogResponse(DoseLogBase):
    id: str

    class Config:
        from_attributes = True
