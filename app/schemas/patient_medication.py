import uuid
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

from app.schemas.medication import MedicationResponse
from app.schemas.schedule import ScheduleResponse


class PatientMedicationFields(BaseModel):
    user_id: uuid.UUID
    medication_id: uuid.UUID
    custom_name: str
    initial_stock: int
    current_stock: int
    stock_warning_threshold: int
    tablets_per_use: int = Field(..., ge=1)
    is_active: bool

    class Config:
        from_attributes = True


class PatientMedicationUpdate(BaseModel):
    custom_name: str | None = None
    current_stock: int | None = None
    stock_warning_threshold: int | None = None
    is_active: bool | None = None


class PatientMedicationResponse(PatientMedicationFields):
    id: uuid.UUID
    medication: MedicationResponse | None = None
    schedules: list[ScheduleResponse] | None = None


class ScheduleDateTimesPayload(BaseModel):
    times: list[datetime] = Field(..., min_length=1)

    @field_validator("times")
    @classmethod
    def validate_times(cls, v: list[datetime]):
        if any(dt.tzinfo is None for dt in v):
            raise ValueError("All times must be timezone-aware datetimes")

        if len(set(v)) != len(v):
            raise ValueError("Duplicate datetimes are not allowed")

        return v


class PatientMedicationWithScheduleCreate(BaseModel):
    medication_id: uuid.UUID
    custom_name: str | None = None

    tablets_per_use: int = Field(1, ge=1)
    initial_stock: int = Field(..., ge=1)

    schedule: ScheduleDateTimesPayload
