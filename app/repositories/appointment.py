from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.appointment import Appointment, AppointmentStatusEnum


class AppointmentRepository:

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Appointment]:
        return db.query(Appointment).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, appointment_id: int) -> Appointment | None:
        return db.query(Appointment).filter(Appointment.id == appointment_id).first()

    @staticmethod
    def get_by_doctor(
        db: Session,
        doctor_id: int,
        skip: int = 0,
        limit: int = 100,
        status: AppointmentStatusEnum | None = None
    ) -> list[Appointment]:
        """Get all appointments for a specific doctor."""
        query = db.query(Appointment).filter(Appointment.doctor_id == doctor_id)
        if status:
            query = query.filter(Appointment.status == status)
        return query.order_by(Appointment.appointment_datetime).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_patient(
        db: Session,
        patient_id: int,
        skip: int = 0,
        limit: int = 100,
        status: AppointmentStatusEnum | None = None
    ) -> list[Appointment]:
        """Get all appointments for a specific patient."""
        query = db.query(Appointment).filter(Appointment.patient_id == patient_id)
        if status:
            query = query.filter(Appointment.status == status)
        return query.order_by(Appointment.appointment_datetime).offset(skip).limit(limit).all()

    @staticmethod
    def get_free_appointments(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        doctor_id: int | None = None,
        from_datetime: datetime | None = None
    ) -> list[Appointment]:
        """Get available (free) appointments for booking."""
        query = db.query(Appointment).filter(Appointment.status == AppointmentStatusEnum.FREE)

        if doctor_id:
            query = query.filter(Appointment.doctor_id == doctor_id)

        if from_datetime:
            query = query.filter(Appointment.appointment_datetime >= from_datetime)
        else:
            # By default, only show future appointments
            query = query.filter(Appointment.appointment_datetime >= datetime.now())

        return query.order_by(Appointment.appointment_datetime).offset(skip).limit(limit).all()

    @staticmethod
    def check_doctor_availability(
        db: Session,
        doctor_id: int,
        appointment_datetime: datetime,
        exclude_appointment_id: int | None = None
    ) -> bool:
        """Check if a doctor has any overlapping appointments at the given time."""
        query = db.query(Appointment).filter(
            and_(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_datetime == appointment_datetime,
                Appointment.status.notin_([AppointmentStatusEnum.CANCELLED])
            )
        )

        if exclude_appointment_id:
            query = query.filter(Appointment.id != exclude_appointment_id)

        return query.first() is None

    @staticmethod
    def create(db: Session, appointment: Appointment) -> Appointment:
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        return appointment

    @staticmethod
    def update(db: Session, appointment: Appointment) -> Appointment:
        db.commit()
        db.refresh(appointment)
        return appointment

    @staticmethod
    def delete(db: Session, appointment: Appointment) -> None:
        db.delete(appointment)
        db.commit()
