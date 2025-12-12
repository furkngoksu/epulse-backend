import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.appointment import Appointment, AppointmentStatusEnum


class AppointmentRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Appointment]:
        return self.db.query(Appointment).offset(skip).limit(limit).all()

    def get_by_id(self, appointment_id: uuid.UUID) -> Appointment | None:
        return self.db.query(Appointment).filter(Appointment.id == appointment_id).first()

    def get_by_doctor(
        self,
        doctor_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        status: AppointmentStatusEnum | None = None
    ) -> list[Appointment]:
        """Get all appointments for a specific doctor."""
        query = self.db.query(Appointment).filter(Appointment.doctor_id == doctor_id)
        if status:
            query = query.filter(Appointment.status == status)
        return query.order_by(Appointment.appointment_datetime).offset(skip).limit(limit).all()

    def get_by_patient(
        self,
        patient_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        status: AppointmentStatusEnum | None = None
    ) -> list[Appointment]:
        """Get all appointments for a specific patient."""
        query = self.db.query(Appointment).filter(Appointment.patient_id == patient_id)
        if status:
            query = query.filter(Appointment.status == status)
        return query.order_by(Appointment.appointment_datetime).offset(skip).limit(limit).all()

    def get_free_appointments(
        self,
        skip: int = 0,
        limit: int = 100,
        doctor_id: uuid.UUID | None = None,
        from_datetime: datetime | None = None
    ) -> list[Appointment]:
        """Get available (free) appointments for booking."""
        query = self.db.query(Appointment).filter(Appointment.status == AppointmentStatusEnum.FREE)

        if doctor_id:
            query = query.filter(Appointment.doctor_id == doctor_id)

        if from_datetime:
            query = query.filter(Appointment.appointment_datetime >= from_datetime)
        else:
            # By default, only show future appointments
            query = query.filter(Appointment.appointment_datetime >= datetime.now())

        return query.order_by(Appointment.appointment_datetime).offset(skip).limit(limit).all()

    def check_doctor_availability(
        self,
        doctor_id: uuid.UUID,
        appointment_datetime: datetime,
        exclude_appointment_id: uuid.UUID | None = None
    ) -> bool:
        """Check if a doctor has any overlapping appointments at the given time."""
        query = self.db.query(Appointment).filter(
            and_(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_datetime == appointment_datetime,
                Appointment.status.notin_([AppointmentStatusEnum.CANCELLED])
            )
        )

        if exclude_appointment_id:
            query = query.filter(Appointment.id != exclude_appointment_id)

        return query.first() is None

    def create(self, appointment: Appointment) -> Appointment:
        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)
        return appointment

    def update(self, appointment: Appointment) -> Appointment:
        self.db.commit()
        self.db.refresh(appointment)
        return appointment

    def delete(self, appointment: Appointment) -> None:
        self.db.delete(appointment)
        self.db.commit()
