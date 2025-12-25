import uuid
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from app.models.appointment import Appointment, AppointmentStatusEnum
from app.models.user import UserModel
from app.models.doctor_profile import DoctorProfile
from app.models.clinic import Clinic
from app.models.hospital import Hospital


class AppointmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def _apply_eager_loading(self, query):
        """Apply eager loading for all appointment relationships."""
        return query.options(
            joinedload(Appointment.doctor)
            .joinedload(UserModel.doctor_profile)
            .joinedload(DoctorProfile.clinic)
            .joinedload(Clinic.hospital),
            joinedload(Appointment.patient),
        )

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Appointment]:
        query = self.db.query(Appointment)
        query = self._apply_eager_loading(query)
        return query.offset(skip).limit(limit).all()

    def get_by_id(self, appointment_id: uuid.UUID) -> Appointment | None:
        query = self.db.query(Appointment).filter(Appointment.id == appointment_id)
        query = self._apply_eager_loading(query)
        return query.first()

    def get_by_doctor(
        self,
        doctor_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        status: AppointmentStatusEnum | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> list[Appointment]:
        """Get all appointments for a specific doctor."""
        query = self.db.query(Appointment).filter(Appointment.doctor_id == doctor_id)
        query = self._apply_eager_loading(query)
        if status:
            query = query.filter(Appointment.status == status)
        if from_date:
            query = query.filter(Appointment.appointment_datetime >= from_date)
        if to_date:
            # Include the entire day by adding 23:59:59
            to_datetime = datetime.combine(
                to_date.date() if isinstance(to_date, datetime) else to_date,
                datetime.max.time(),
            )
            query = query.filter(Appointment.appointment_datetime <= to_datetime)
        return (
            query.order_by(Appointment.appointment_datetime)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_patient(
        self,
        patient_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        status: AppointmentStatusEnum | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> list[Appointment]:
        """Get all appointments for a specific patient."""
        query = self.db.query(Appointment).filter(Appointment.patient_id == patient_id)
        query = self._apply_eager_loading(query)
        if status:
            query = query.filter(Appointment.status == status)
        if from_date:
            query = query.filter(Appointment.appointment_datetime >= from_date)
        if to_date:
            # Include the entire day by adding 23:59:59
            to_datetime = datetime.combine(
                to_date.date() if isinstance(to_date, datetime) else to_date,
                datetime.max.time(),
            )
            query = query.filter(Appointment.appointment_datetime <= to_datetime)
        return (
            query.order_by(Appointment.appointment_datetime)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_free_appointments(
        self,
        skip: int = 0,
        limit: int = 100,
        doctor_id: uuid.UUID | None = None,
        from_datetime: datetime | None = None,
    ) -> list[Appointment]:
        """Get available (free) appointments for booking."""
        query = self.db.query(Appointment).filter(
            Appointment.status == AppointmentStatusEnum.free
        )
        query = self._apply_eager_loading(query)

        if doctor_id:
            query = query.filter(Appointment.doctor_id == doctor_id)

        if from_datetime:
            query = query.filter(Appointment.appointment_datetime >= from_datetime)
        else:
            # By default, only show future appointments
            query = query.filter(Appointment.appointment_datetime >= datetime.now())

        return (
            query.order_by(Appointment.appointment_datetime)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def check_doctor_availability(
        self,
        doctor_id: uuid.UUID,
        appointment_datetime: datetime,
        exclude_appointment_id: uuid.UUID | None = None,
    ) -> bool:
        """Check if a doctor has any overlapping appointments at the given time."""
        query = self.db.query(Appointment).filter(
            and_(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_datetime == appointment_datetime,
                Appointment.status.notin_([AppointmentStatusEnum.cancelled]),
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

    def search_free_appointments(
        self,
        city: str,
        clinic_name: str,
        district: str | None = None,
        hospital_id: uuid.UUID | None = None,
        doctor_id: uuid.UUID | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Appointment]:
        """Search for free appointments with advanced filtering."""
        # Build query with joins (joins are already done for filtering, now add eager loading)
        query = (
            self.db.query(Appointment)
            .join(UserModel, Appointment.doctor_id == UserModel.id)
            .join(DoctorProfile, UserModel.id == DoctorProfile.id)
            .join(Clinic, DoctorProfile.clinic_id == Clinic.id)
            .join(Hospital, Clinic.hospital_id == Hospital.id)
            .filter(
                Appointment.status == AppointmentStatusEnum.free,
                Hospital.city.ilike(f"%{city}%"),
                Clinic.name.ilike(f"%{clinic_name}%"),
            )
        )
        # Apply eager loading for relationships
        query = self._apply_eager_loading(query)

        # Optional filters
        if district:
            query = query.filter(Hospital.district.ilike(f"%{district}%"))

        if hospital_id:
            query = query.filter(Hospital.id == hospital_id)

        if doctor_id:
            query = query.filter(Appointment.doctor_id == doctor_id)

        if from_date:
            from_datetime = datetime.combine(from_date, datetime.min.time())
            # If from_date is in the past, set it to now + 1 day
            now = datetime.now()
            if from_datetime < now:
                from_datetime = now + timedelta(days=1)
            query = query.filter(Appointment.appointment_datetime >= from_datetime)
        else:
            # By default, only show future appointments
            query = query.filter(Appointment.appointment_datetime >= datetime.now())

        if to_date:
            to_datetime = datetime.combine(to_date, datetime.max.time())
            query = query.filter(Appointment.appointment_datetime <= to_datetime)

        # Order by appointment_datetime ascending (earliest first)
        return (
            query.order_by(Appointment.appointment_datetime)
            .offset(skip)
            .limit(limit)
            .all()
        )
