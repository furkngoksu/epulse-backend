import uuid
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.schedule_time import DoseStatusEnum


class ScheduleTimeCreate(BaseModel):
    dose_datetime: datetime


class ScheduleTimeResponse(BaseModel):
    id: uuid.UUID
    dose_datetime: datetime
    status: DoseStatusEnum
    taken_at: datetime | None
    skip_reason: str | None

    class Config:
        from_attributes = True


class MarkDoseTakenRequest(BaseModel):
    taken_at: datetime | None = None


class MarkDoseSkippedRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=255)
