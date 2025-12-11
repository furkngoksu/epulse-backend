import uuid
from datetime import datetime

from app.models.appointment import Appointment, AppointmentStatusEnum
from app.models.user import RoleEnum
from app.models.doctor_patient_relationship import DoctorPatientRelationship
from app.repositories.appointment import AppointmentRepository
from app.repositories.user import UserRepository
from app.repositories.doctor_patient_relationship import DoctorPatientRelationshipRepository
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentBook
from app.exceptions.exceptions import NotFoundException, BadRequestException, ConflictException


class AppointmentService:

    def __init__(
        self,
        appointment_repository: AppointmentRepository,
        user_repository: UserRepository,
        doctor_patient_relationship_repository: DoctorPatientRelationshipRepository
    ):
        self.appointment_repository = appointment_repository
        self.user_repository = user_repository
        self.doctor_patient_relationship_repository = doctor_patient_relationship_repository

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Appointment]:
        return self.appointment_repository.get_all(skip=skip, limit=limit)

    def get_by_id(self, appointment_id: uuid.UUID) -> Appointment:
        appointment = self.appointment_repository.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException("Appointment not found")
        return appointment

    def get_by_doctor(
        self,
        doctor_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        status: AppointmentStatusEnum | None = None
    ) -> list[Appointment]:
        """Get all appointments for a specific doctor."""
        # Verify doctor exists and has doctor role
        doctor = self.user_repository.get_by_id(doctor_id)
        if not doctor:
            raise NotFoundException("Doctor not found")
        if doctor.role != RoleEnum.DOCTOR:
            raise BadRequestException("User is not a doctor")

        return self.appointment_repository.get_by_doctor(doctor_id, skip, limit, status)

    def get_by_patient(
        self,
        patient_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        status: AppointmentStatusEnum | None = None
    ) -> list[Appointment]:
        """Get all appointments for a specific patient."""
        # Verify patient exists and has patient role
        patient = self.user_repository.get_by_id(patient_id)
        if not patient:
            raise NotFoundException("Patient not found")
        if patient.role != RoleEnum.PATIENT:
            raise BadRequestException("User is not a patient")

        return self.appointment_repository.get_by_patient(patient_id, skip, limit, status)

    def get_free_appointments(
        self,
        skip: int = 0,
        limit: int = 100,
        doctor_id: uuid.UUID | None = None,
        from_datetime: datetime | None = None
    ) -> list[Appointment]:
        """Get available appointments for booking."""
        if doctor_id:
            # Verify doctor exists and has doctor role
            doctor = self.user_repository.get_by_id(doctor_id)
            if not doctor:
                raise NotFoundException("Doctor not found")
            if doctor.role != RoleEnum.DOCTOR:
                raise BadRequestException("User is not a doctor")

        return self.appointment_repository.get_free_appointments(
            skip=skip, limit=limit, doctor_id=doctor_id, from_datetime=from_datetime
        )

    def create(self, data: AppointmentCreate) -> Appointment:
        """Create a new free appointment slot."""
        # Validate doctor exists and has doctor role
        doctor = self.user_repository.get_by_id(data.doctor_id)
        if not doctor:
            raise NotFoundException(f"Doctor with id {data.doctor_id} not found")
        if doctor.role != RoleEnum.DOCTOR:
            raise BadRequestException(f"User with id {data.doctor_id} is not a doctor")

        # Validate appointment is not in the past
        if data.appointment_datetime < datetime.now():
            raise BadRequestException("Cannot create appointment in the past")

        # Check if doctor already has an appointment at this time
        if not self.appointment_repository.check_doctor_availability(data.doctor_id, data.appointment_datetime):
            raise ConflictException("Doctor already has an appointment at this time")

        appointment = Appointment(
            doctor_id=data.doctor_id,
            appointment_datetime=data.appointment_datetime,
            facility_name=data.facility_name,
            notes=data.notes,
            status=AppointmentStatusEnum.FREE
        )
        return self.appointment_repository.create(appointment)

    def book(self, appointment_id: uuid.UUID, patient_id: uuid.UUID, data: AppointmentBook) -> Appointment:
        """Patient books a free appointment."""
        appointment = self.appointment_repository.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException("Appointment not found")

        # Validate patient exists and has patient role
        patient = self.user_repository.get_by_id(patient_id)
        if not patient:
            raise NotFoundException(f"Patient with id {patient_id} not found")
        if patient.role != RoleEnum.PATIENT:
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
        existing_relationship = self.doctor_patient_relationship_repository.get_by_doctor_and_patient(
            appointment.doctor_id, patient_id
        )
        if not existing_relationship:
            relationship = DoctorPatientRelationship(
                doctor_id=appointment.doctor_id,
                patient_id=patient_id
            )
            self.doctor_patient_relationship_repository.create(relationship)

        return self.appointment_repository.update(appointment)

    def patient_cancel(self, appointment_id: uuid.UUID, patient_id: uuid.UUID) -> Appointment:
        """Patient cancels their booked appointment (reverts to free)."""
        appointment = self.appointment_repository.get_by_id(appointment_id)
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

        return self.appointment_repository.update(appointment)

    def admin_cancel(self, appointment_id: uuid.UUID) -> Appointment:
        """Admin or doctor cancels an appointment (permanent cancellation)."""
        appointment = self.appointment_repository.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException("Appointment not found")

        # Check if appointment can be cancelled
        if appointment.status in [AppointmentStatusEnum.COMPLETED, AppointmentStatusEnum.NO_SHOW]:
            raise BadRequestException(f"Cannot cancel appointment with status: {appointment.status.value}")

        if appointment.status == AppointmentStatusEnum.CANCELLED:
            raise BadRequestException("Appointment is already cancelled")

        appointment.status = AppointmentStatusEnum.CANCELLED

        return self.appointment_repository.update(appointment)

    def complete(self, appointment_id: uuid.UUID) -> Appointment:
        """Mark an appointment as completed."""
        appointment = self.appointment_repository.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException("Appointment not found")

        # Check if appointment can be completed
        if appointment.status != AppointmentStatusEnum.BOOKED:
            raise BadRequestException(f"Only booked appointments can be completed (current status: {appointment.status.value})")

        appointment.status = AppointmentStatusEnum.COMPLETED

        return self.appointment_repository.update(appointment)

    def no_show(self, appointment_id: uuid.UUID) -> Appointment:
        """Mark an appointment as no-show (patient did not attend)."""
        appointment = self.appointment_repository.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException("Appointment not found")

        # Check if appointment can be marked as no-show
        if appointment.status != AppointmentStatusEnum.BOOKED:
            raise BadRequestException(f"Only booked appointments can be marked as no-show (current status: {appointment.status.value})")

        appointment.status = AppointmentStatusEnum.NO_SHOW

        return self.appointment_repository.update(appointment)

    def update(self, appointment_id: uuid.UUID, data: AppointmentUpdate) -> Appointment:
        """Update appointment details (admin only)."""
        appointment = self.appointment_repository.get_by_id(appointment_id)
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
            if not self.appointment_repository.check_doctor_availability(
                appointment.doctor_id, data.appointment_datetime, appointment.id
            ):
                raise ConflictException("Doctor already has an appointment at this time")

            appointment.appointment_datetime = data.appointment_datetime

        if data.facility_name is not None:
            appointment.facility_name = data.facility_name

        if data.notes is not None:
            appointment.notes = data.notes

        return self.appointment_repository.update(appointment)

    def delete(self, appointment_id: uuid.UUID) -> None:
        """Delete an appointment (admin only)."""
        appointment = self.appointment_repository.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException("Appointment not found")
        self.appointment_repository.delete(appointment)
