import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps.services import get_appointment_service
from app.api.deps.auth import get_current_user, get_current_admin
from app.schemas.user import User, RoleEnum
from app.models.appointment import AppointmentStatusEnum
from app.models.user import UserModel
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentBook,
    AppointmentResponse
)
from app.services.appointment_service import AppointmentService
from app.exceptions.exceptions import ForbiddenException

router = APIRouter()


@router.get("/", response_model=list[AppointmentResponse])
def get_all_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    appointment_service: AppointmentService = Depends(get_appointment_service),
    current_user: UserModel = Depends(get_current_admin)
):
    """
    Get all appointments.
    Requires admin role.
    """
    appointments = appointment_service.get_all(skip=skip, limit=limit)
    return appointments


@router.get("/free", response_model=list[AppointmentResponse])
def get_free_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    doctor_id: uuid.UUID | None = Query(None),
    from_datetime: datetime | None = None,
    appointment_service: AppointmentService = Depends(get_appointment_service),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get available appointments for booking.
    Requires authentication.
    """
    appointments = appointment_service.get_free_appointments(
        skip=skip, limit=limit, doctor_id=doctor_id, from_datetime=from_datetime
    )
    return appointments


@router.get("/doctor/{doctor_id}", response_model=list[AppointmentResponse])
def get_appointments_by_doctor(
    doctor_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: AppointmentStatusEnum | None = None,
    appointment_service: AppointmentService = Depends(get_appointment_service),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get all appointments for a specific doctor.
    Doctors can only view their own appointments. Admins can view any doctor's appointments.
    """
    # Only admins and doctors can access this endpoint
    if current_user.role == RoleEnum.PATIENT:
        raise ForbiddenException("Patients cannot view doctor appointment lists")

    # Doctors can only view their own appointments
    if current_user.role == RoleEnum.DOCTOR and current_user.id != doctor_id:
        raise ForbiddenException("You can only view your own appointments")

    appointments = appointment_service.get_by_doctor(
        doctor_id, skip=skip, limit=limit, status=status
    )
    return appointments


@router.get("/patient/{patient_id}", response_model=list[AppointmentResponse])
def get_appointments_by_patient(
    patient_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: AppointmentStatusEnum | None = None,
    appointment_service: AppointmentService = Depends(get_appointment_service),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get all appointments for a specific patient.
    Patients can only view their own appointments. Admins can view any patient's appointments.
    """
    # Only admins and patients can access this endpoint
    if current_user.role == RoleEnum.DOCTOR:
        raise ForbiddenException("Doctors cannot view patient appointment lists")

    # Patients can only view their own appointments
    if current_user.role == RoleEnum.PATIENT and current_user.id != patient_id:
        raise ForbiddenException("You can only view your own appointments")

    appointments = appointment_service.get_by_patient(
        patient_id, skip=skip, limit=limit, status=status
    )
    return appointments


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: uuid.UUID,
    appointment_service: AppointmentService = Depends(get_appointment_service),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get an appointment by ID.
    Requires authentication.
    """
    appointment = appointment_service.get_by_id(appointment_id)

    # Check access - patients can only see their own appointments
    if current_user.role == RoleEnum.PATIENT:
        if appointment.patient_id != current_user.id:
            raise ForbiddenException("You can only view your own appointments")

    # Doctors can only see their own appointments
    if current_user.role == RoleEnum.DOCTOR:
        if appointment.doctor_id != current_user.id:
            raise ForbiddenException("You can only view your own appointments")

    return appointment


@router.post("/", response_model=AppointmentResponse, status_code=201)
def create_appointment(
    data: AppointmentCreate,
    appointment_service: AppointmentService = Depends(get_appointment_service),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Create a new free appointment slot.
    Doctors can create appointments for themselves. Admins can create for any doctor.
    """
    # Only doctors and admins can create appointments
    if current_user.role == RoleEnum.PATIENT:
        raise ForbiddenException("Patients cannot create appointments")

    # Doctors can only create appointments for themselves
    if current_user.role == RoleEnum.DOCTOR and current_user.id != data.doctor_id:
        raise ForbiddenException("You can only create appointments for yourself")

    appointment = appointment_service.create(data)
    return appointment


@router.post("/{appointment_id}/book", response_model=AppointmentResponse)
def book_appointment(
    appointment_id: uuid.UUID,
    data: AppointmentBook,
    appointment_service: AppointmentService = Depends(get_appointment_service),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Book a free appointment.
    Only patients can book appointments.
    """
    # Only patients can book appointments
    if current_user.role != RoleEnum.PATIENT:
        raise ForbiddenException("Only patients can book appointments")

    appointment = appointment_service.book(appointment_id, current_user.id, data)
    return appointment


@router.post("/{appointment_id}/cancel", response_model=AppointmentResponse)
def cancel_appointment(
    appointment_id: uuid.UUID,
    appointment_service: AppointmentService = Depends(get_appointment_service),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Cancel an appointment.
    - Patients can cancel their own booked appointments (reverts to free status).
    - Doctors can cancel their own appointments (permanent cancellation).
    - Admins can cancel any appointment (permanent cancellation).
    """
    appointment = appointment_service.get_by_id(appointment_id)

    # Patient cancellation - reverts to free
    if current_user.role == RoleEnum.PATIENT:
        if appointment.patient_id != current_user.id:
            raise ForbiddenException("You can only cancel your own appointments")
        return appointment_service.patient_cancel(appointment_id, current_user.id)

    # Doctor cancellation - permanent
    if current_user.role == RoleEnum.DOCTOR:
        if appointment.doctor_id != current_user.id:
            raise ForbiddenException("You can only cancel your own appointments")
        return appointment_service.admin_cancel(appointment_id)

    # Admin cancellation - permanent
    return appointment_service.admin_cancel(appointment_id)


@router.post("/{appointment_id}/complete", response_model=AppointmentResponse)
def complete_appointment(
    appointment_id: uuid.UUID,
    appointment_service: AppointmentService = Depends(get_appointment_service),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Mark an appointment as completed.
    Doctors can complete their own appointments. Admins can complete any appointment.
    """
    # Only doctors and admins can complete appointments
    if current_user.role == RoleEnum.PATIENT:
        raise ForbiddenException("Patients cannot mark appointments as completed")

    appointment = appointment_service.get_by_id(appointment_id)

    # Doctors can only complete their own appointments
    if current_user.role == RoleEnum.DOCTOR and appointment.doctor_id != current_user.id:
        raise ForbiddenException("You can only complete your own appointments")

    return appointment_service.complete(appointment_id)


@router.post("/{appointment_id}/no-show", response_model=AppointmentResponse)
def mark_no_show(
    appointment_id: uuid.UUID,
    appointment_service: AppointmentService = Depends(get_appointment_service),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Mark an appointment as no-show (patient did not attend).
    Doctors can mark their own appointments. Admins can mark any appointment.
    """
    # Only doctors and admins can mark as no-show
    if current_user.role == RoleEnum.PATIENT:
        raise ForbiddenException("Patients cannot mark appointments as no-show")

    appointment = appointment_service.get_by_id(appointment_id)

    # Doctors can only mark their own appointments
    if current_user.role == RoleEnum.DOCTOR and appointment.doctor_id != current_user.id:
        raise ForbiddenException("You can only mark your own appointments as no-show")

    return appointment_service.no_show(appointment_id)


@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: uuid.UUID,
    data: AppointmentUpdate,
    appointment_service: AppointmentService = Depends(get_appointment_service),
    current_user: UserModel = Depends(get_current_admin)
):
    """
    Update appointment details.
    Requires admin role.
    """
    appointment = appointment_service.update(appointment_id, data)
    return appointment


@router.delete("/{appointment_id}", status_code=204)
def delete_appointment(
    appointment_id: uuid.UUID,
    appointment_service: AppointmentService = Depends(get_appointment_service),
    current_user: UserModel = Depends(get_current_admin)
):
    """
    Delete an appointment.
    Requires admin role.
    """
    appointment_service.delete(appointment_id)
