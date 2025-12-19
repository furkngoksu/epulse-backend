import uuid
from datetime import datetime, date, time
from pydantic import BaseModel, Field
from app.models.appointment import AppointmentStatusEnum


class AppointmentBase(BaseModel):
    doctor_id: uuid.UUID
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


class CreateFreeAppointmentsRequest(BaseModel):
    """Schema for creating multiple free appointment slots."""
    doctor_id: uuid.UUID
    dates: list[date] = Field(..., min_length=1)
    time_slots: list[time] = Field(..., min_length=1)
    facility_name: str = Field(..., min_length=1, max_length=200)


class AppointmentResponse(AppointmentBase):
    id: uuid.UUID
    patient_id: uuid.UUID | None = None
    status: AppointmentStatusEnum

    class Config:
        from_attributes = True
