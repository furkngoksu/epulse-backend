import uuid
from datetime import date
from pydantic import BaseModel

from app.schemas.schedule_time import ScheduleTimeResponse


class ScheduleBase(BaseModel):
    patient_medication_id: uuid.UUID
    start_date: date
    end_date: date


class ScheduleCreate(ScheduleBase):
    pass


class ScheduleResponse(ScheduleBase):
    id: uuid.UUID
    schedule_times: list[ScheduleTimeResponse] | None = None

    class Config:
        from_attributes = True
