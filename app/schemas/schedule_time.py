from pydantic import BaseModel
import uuid

class ScheduleTimeBase(BaseModel):
    schedule_id:  uuid.UUID
    start_time: str
    end_time: str

class ScheduleTimeUpdate(ScheduleTimeBase):
    pass

class ScheduleTimeCreate(ScheduleTimeBase):
    pass


class ScheduleTimeResponse(ScheduleTimeBase):
    id: uuid.UUID

    class Config:
        from_attributes = True