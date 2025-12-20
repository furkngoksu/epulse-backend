from datetime import datetime
from pydantic import BaseModel
import uuid

from app.schemas.schedule_time import ScheduleTimeResponse
from app.models.schedule import FrequencyTypeEnum

class ScheduleBase(BaseModel):
    patient_medication_id: uuid.UUID
    start_date: datetime
    end_date: datetime
    frequency_type: FrequencyTypeEnum | None = None
    specific_days: dict | None = None


class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(ScheduleBase):
    id: uuid.UUID

class ScheduleResponse(ScheduleBase):
    id: uuid.UUID

    schedule_times  : list[ScheduleTimeResponse] | None = None

    class Config:
        from_attributes = True

