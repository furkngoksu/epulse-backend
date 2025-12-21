import uuid
from datetime import datetime, date, time
from pydantic import BaseModel, Field, model_validator
from typing import Any
from app.models.appointment import AppointmentStatusEnum


class AppointmentBase(BaseModel):
    doctor_id: uuid.UUID
    appointment_datetime: datetime
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
    notes: str | None = None


class CreateFreeAppointmentsRequest(BaseModel):
    """Schema for creating multiple free appointment slots."""
    doctor_id: uuid.UUID
    dates: list[date] = Field(..., min_length=1)
    time_slots: list[time] = Field(..., min_length=1)


class AppointmentResponse(BaseModel):
    id: uuid.UUID
    hospital_name: str
    clinic_name: str
    city: str
    district: str
    doctor_id: uuid.UUID
    doctor_name: str
    patient_id: uuid.UUID | None = None
    patient_name: str | None = None
    appointment_datetime: datetime
    notes: str | None = None
    status: AppointmentStatusEnum

    @model_validator(mode='before')
    @classmethod
    def compute_fields(cls, data: Any) -> dict:
        """Compute derived fields from ORM relationships."""
        if hasattr(data, '__dict__'):  # It's an ORM object
            appointment = data

            # Get doctor information
            doctor = appointment.doctor
            doctor_name = f"{doctor.first_name} {doctor.last_name}"

            # Get clinic and hospital information through doctor_profile
            clinic = doctor.doctor_profile.clinic
            hospital = clinic.hospital

            # Get patient information if exists
            patient_name = None
            if appointment.patient_id and appointment.patient:
                patient = appointment.patient
                patient_name = f"{patient.first_name} {patient.last_name}"

            return {
                'id': appointment.id,
                'hospital_name': hospital.name,
                'clinic_name': clinic.name,
                'city': hospital.city,
                'district': hospital.district,
                'doctor_id': appointment.doctor_id,
                'doctor_name': doctor_name,
                'patient_id': appointment.patient_id,
                'patient_name': patient_name,
                'appointment_datetime': appointment.appointment_datetime,
                'notes': appointment.notes,
                'status': appointment.status,
            }
        return data

    class Config:
        from_attributes = True
