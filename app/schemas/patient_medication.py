import uuid
from pydantic import BaseModel, Field , field_validator

from app.models.schedule import FrequencyTypeEnum
from app.schemas.medication import MedicationResponse
from app.schemas.schedule import ScheduleResponse
from datetime import datetime

class PatientMedicationBase(BaseModel):
    user_id: uuid.UUID
    medication_id: uuid.UUID
    custom_name: str
    initial_stock: int = 0
    current_stock: int = 0
    stock_warning_threshold: int = 0
    tablets_per_use: int = Field(...)
    is_active: bool = False


class PatientMedicationCreate(PatientMedicationBase):
    pass


class PatientMedicationUpdate(BaseModel):
    custom_name: str | None = None
    initial_stock: int | None = None
    current_stock: int | None = None
    stock_warning_threshold: int | None = None
    is_active: bool | None = None


class PatientMedicationResponse(PatientMedicationBase):
    id: uuid.UUID

    medication: MedicationResponse | None = None
    schedules: list[ScheduleResponse] | None = None

    class Config:
        from_attributes = True

class ScheduleTimesPayload(BaseModel):
    times: list[datetime] = Field(..., min_length=1)

    @field_validator("times")
    @classmethod
    def validate_times(cls, v: list[datetime]):
        # timezone aware olsun (DB timezone=True)
        if any(dt.tzinfo is None for dt in v):
            raise ValueError("All times must be timezone-aware datetimes")
        # duplicate engelle (aynı dt iki kere)
        if len(set(v)) != len(v):
            raise ValueError("Duplicate dose datetimes are not allowed")
        return v


class PatientMedicationWithScheduleCreate(BaseModel):
    medication_id: uuid.UUID
    custom_name: str | None = None

    tablets_per_use: int = Field(1, ge=1)

    # Sen “initial_stock DB’den çekilecek” diyordun.
    # MedicationModel'de bu alan yoksa şimdilik request’ten al.
    initial_stock: int = Field(..., ge=1)

    start_date: datetime
    end_date: datetime

    frequency_type: FrequencyTypeEnum | None = None
    specific_days: dict | None = None

    schedule: ScheduleTimesPayload

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_tz(cls, v: datetime):
        if v.tzinfo is None:
            raise ValueError("start_date/end_date must be timezone-aware")
        return v

    @field_validator("end_date")
    @classmethod
    def validate_range(cls, end_date: datetime, info):
        start_date = info.data.get("start_date")
        if start_date and end_date < start_date:
            raise ValueError("end_date cannot be earlier than start_date")
        return end_date


class PatientMedicationCreatedResponse(BaseModel):
    patient_medication_id: uuid.UUID
