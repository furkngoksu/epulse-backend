import uuid
from pydantic import BaseModel, Field

from app.schemas.dose_log import DoseLogResponse
from app.schemas.medication import MedicationResponse
from app.schemas.schedule import ScheduleResponse

class PatientMedicationBase(BaseModel):
    user_id: uuid.UUID = Field(...)
    medication_id: uuid.UUID = Field(...)
    custom_name: str = Field(...)
    initial_stock: int = Field(default=0)
    current_stock: int = Field(default=0)
    stock_warning_threshold: int = Field(default=0)
    is_active: bool = Field(default=False)


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
    dose_logs: list[DoseLogResponse] | None = None

    class Config:
        from_attributes = True
