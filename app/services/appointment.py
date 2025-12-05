from datetime import datetime
from sqlalchemy.orm import Session

from app.models.appointment import Appointment, AppointmentStatusEnum
from app.models.user import RoleEnum
from app.repositories.appointment import AppointmentRepository
from app.repositories.user import UserRepository
from app.repositories.doctor_patient_relationship import DoctorPatientRelationshipRepository
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentBook
from app.schemas.doctor_patient_relationship import DoctorPatientRelationshipCreate
from app.services.doctor_service import DoctorService
from app.exceptions.exceptions import NotFoundException, BadRequestException, ConflictException


class AppointmentService:

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Appointment]:
        return AppointmentRepository.get_all(db, skip=skip, limit=limit)

    @staticmethod
    def get_by_id(db: Session, appointment_id: int) -> Appointment:
        appointment = AppointmentRepository.get_by_id(db, appointment_id)
        if not appointment:
            raise NotFoundException("Appointment not found")
        return appointment

    @staticmethod
    def get_by_doctor(
        db: Session,
        doctor_id: int,
        skip: int = 0,
        limit: int = 100,
        status: AppointmentStatusEnum | None = None
    ) -> list[Appointment]:
        """Get all appointments for a specific doctor."""
        # Verify doctor exists and has doctor role
        doctor = UserRepository.get_by_id(db, doctor_id)
        if not doctor:
            raise NotFoundException("Doctor not found")
        if doctor.role != RoleEnum.doctor:
            raise BadRequestException("User is not a doctor")

        return AppointmentRepository.get_by_doctor(db, doctor_id, skip, limit, status)

    @staticmethod
    def get_by_patient(
        db: Session,
        patient_id: int,
        skip: int = 0,
        limit: int = 100,
        status: AppointmentStatusEnum | None = None
    ) -> list[Appointment]:
        """Get all appointments for a specific patient."""
        # Verify patient exists and has patient role
        patient = UserRepository.get_by_id(db, patient_id)
        if not patient:
            raise NotFoundException("Patient not found")
        if patient.role != RoleEnum.patient:
            raise BadRequestException("User is not a patient")

        return AppointmentRepository.get_by_patient(db, patient_id, skip, limit, status)

    @staticmethod
    def get_free_appointments(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        doctor_id: int | None = None,
        from_datetime: datetime | None = None
    ) -> list[Appointment]:
        """Get available appointments for booking."""
        if doctor_id:
            # Verify doctor exists and has doctor role
            doctor = UserRepository.get_by_id(db, doctor_id)
            if not doctor:
                raise NotFoundException("Doctor not found")
            if doctor.role != RoleEnum.doctor:
                raise BadRequestException("User is not a doctor")

        return AppointmentRepository.get_free_appointments(
            db, skip=skip, limit=limit, doctor_id=doctor_id, from_datetime=from_datetime
        )

    @staticmethod
    def create(db: Session, data: AppointmentCreate) -> Appointment:
        """Create a new free appointment slot."""
        # Validate doctor exists and has doctor role
        doctor = UserRepository.get_by_id(db, data.doctor_id)
        if not doctor:
            raise NotFoundException(f"Doctor with id {data.doctor_id} not found")
        if doctor.role != RoleEnum.doctor:
            raise BadRequestException(f"User with id {data.doctor_id} is not a doctor")

        # Validate appointment is not in the past
        if data.appointment_datetime < datetime.now():
            raise BadRequestException("Cannot create appointment in the past")

        # Check if doctor already has an appointment at this time
        if not AppointmentRepository.check_doctor_availability(db, data.doctor_id, data.appointment_datetime):
            raise ConflictException("Doctor already has an appointment at this time")

        appointment = Appointment(
            doctor_id=data.doctor_id,
            appointment_datetime=data.appointment_datetime,
            facility_name=data.facility_name,
            notes=data.notes,
            status=AppointmentStatusEnum.FREE
        )
        return AppointmentRepository.create(db, appointment)

    @staticmethod
    def book(db: Session, appointment_id: int, patient_id: int, data: AppointmentBook) -> Appointment:
        """Patient books a free appointment."""
        appointment = AppointmentRepository.get_by_id(db, appointment_id)
        if not appointment:
            raise NotFoundException("Appointment not found")

        # Validate patient exists and has patient role
        patient = UserRepository.get_by_id(db, patient_id)
        if not patient:
            raise NotFoundException(f"Patient with id {patient_id} not found")
        if patient.role != RoleEnum.patient:
            raise BadRequestException(f"User with id {patient_id} is not a patient")

        # Check appointment status
        if appointment.status != AppointmentStatusEnum.FREE:
            raise BadRequestException(f"Appointment is not available for booking (status: {appointment.status.value})")

        # Validate appointment is not in the past
        if appointment.appointment_datetime < datetime.now():
            raise BadRequestException("Cannot book appointment in the past")

        # Book the appointment
        appointment.patient_id = patient_id
        appointment.status = AppointmentStatusEnum.BOOKED
        if data.notes:
            appointment.notes = data.notes

        # Create doctor-patient relationship if it doesn't exist
        existing_relationship = DoctorPatientRelationshipRepository.get_by_doctor_and_patient(
            db, appointment.doctor_id, patient_id
        )
        if not existing_relationship:
            relationship_data = DoctorPatientRelationshipCreate(
                doctor_id=appointment.doctor_id,
                patient_id=patient_id
            )
            DoctorService.create_doctor_patient_relationship(db, relationship_data)

        return AppointmentRepository.update(db, appointment)

    @staticmethod
    def patient_cancel(db: Session, appointment_id: int, patient_id: int) -> Appointment:
        """Patient cancels their booked appointment (reverts to free)."""
        appointment = AppointmentRepository.get_by_id(db, appointment_id)
        if not appointment:
            raise NotFoundException("Appointment not found")

        # Verify the patient owns this appointment
        if appointment.patient_id != patient_id:
            raise BadRequestException("This appointment does not belong to you")

        # Check if appointment can be cancelled by patient
        if appointment.status != AppointmentStatusEnum.BOOKED:
            raise BadRequestException(f"Cannot cancel appointment with status: {appointment.status.value}")

        # Validate appointment is not in the past
        if appointment.appointment_datetime < datetime.now():
            raise BadRequestException("Cannot cancel appointment that has already passed")

        # Revert to free status
        appointment.patient_id = None
        appointment.status = AppointmentStatusEnum.FREE
        appointment.notes = None

        return AppointmentRepository.update(db, appointment)

    @staticmethod
    def admin_cancel(db: Session, appointment_id: int) -> Appointment:
        """Admin or doctor cancels an appointment (permanent cancellation)."""
        appointment = AppointmentRepository.get_by_id(db, appointment_id)
        if not appointment:
            raise NotFoundException("Appointment not found")

        # Check if appointment can be cancelled
        if appointment.status in [AppointmentStatusEnum.COMPLETED, AppointmentStatusEnum.NO_SHOW]:
            raise BadRequestException(f"Cannot cancel appointment with status: {appointment.status.value}")

        if appointment.status == AppointmentStatusEnum.CANCELLED:
            raise BadRequestException("Appointment is already cancelled")

        appointment.status = AppointmentStatusEnum.CANCELLED

        return AppointmentRepository.update(db, appointment)

    @staticmethod
    def complete(db: Session, appointment_id: int) -> Appointment:
        """Mark an appointment as completed."""
        appointment = AppointmentRepository.get_by_id(db, appointment_id)
        if not appointment:
            raise NotFoundException("Appointment not found")

        # Check if appointment can be completed
        if appointment.status != AppointmentStatusEnum.BOOKED:
            raise BadRequestException(f"Only booked appointments can be completed (current status: {appointment.status.value})")

        appointment.status = AppointmentStatusEnum.COMPLETED

        return AppointmentRepository.update(db, appointment)

    @staticmethod
    def no_show(db: Session, appointment_id: int) -> Appointment:
        """Mark an appointment as no-show (patient did not attend)."""
        appointment = AppointmentRepository.get_by_id(db, appointment_id)
        if not appointment:
            raise NotFoundException("Appointment not found")

        # Check if appointment can be marked as no-show
        if appointment.status != AppointmentStatusEnum.BOOKED:
            raise BadRequestException(f"Only booked appointments can be marked as no-show (current status: {appointment.status.value})")

        appointment.status = AppointmentStatusEnum.NO_SHOW

        return AppointmentRepository.update(db, appointment)

    @staticmethod
    def update(db: Session, appointment_id: int, data: AppointmentUpdate) -> Appointment:
        """Update appointment details (admin only)."""
        appointment = AppointmentRepository.get_by_id(db, appointment_id)
        if not appointment:
            raise NotFoundException("Appointment not found")

        # Cannot update cancelled, completed, or no_show appointments
        if appointment.status in [AppointmentStatusEnum.CANCELLED, AppointmentStatusEnum.COMPLETED, AppointmentStatusEnum.NO_SHOW]:
            raise BadRequestException(f"Cannot update appointment with status: {appointment.status.value}")

        # Update datetime if provided
        if data.appointment_datetime is not None:
            # Validate not in the past
            if data.appointment_datetime < datetime.now():
                raise BadRequestException("Cannot set appointment time to the past")

            # Check availability (excluding current appointment)
            if not AppointmentRepository.check_doctor_availability(
                db, appointment.doctor_id, data.appointment_datetime, appointment.id
            ):
                raise ConflictException("Doctor already has an appointment at this time")

            appointment.appointment_datetime = data.appointment_datetime

        if data.facility_name is not None:
            appointment.facility_name = data.facility_name

        if data.notes is not None:
            appointment.notes = data.notes

        return AppointmentRepository.update(db, appointment)

    @staticmethod
    def delete(db: Session, appointment_id: int) -> None:
        """Delete an appointment (admin only)."""
        appointment = AppointmentRepository.get_by_id(db, appointment_id)
        if not appointment:
            raise NotFoundException("Appointment not found")
        AppointmentRepository.delete(db, appointment)
