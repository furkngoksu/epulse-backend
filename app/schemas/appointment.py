from datetime import datetime
from pydantic import BaseModel, Field
from app.models.appointment import AppointmentStatusEnum


class AppointmentBase(BaseModel):
    doctor_id: int
    appointment_datetime: datetime
    facility_name: str = Field(..., min_length=1, max_length=200)
    notes: str | None = None


class AppointmentCreate(AppointmentBase):
    """Schema for creating a free appointment slot (by doctor or admin)."""
    pass


class AppointmentBook(BaseModel):
    """Schema for patient booking an appointment."""
    notes: str | None = None


class AppointmentUpdate(BaseModel):
    """Schema for updating appointment details (by admin)."""
    appointment_datetime: datetime | None = None
    facility_name: str | None = Field(None, min_length=1, max_length=200)
    notes: str | None = None


class AppointmentResponse(AppointmentBase):
    id: int
    patient_id: int | None = None
    status: AppointmentStatusEnum

    class Config:
        from_attributes = True
