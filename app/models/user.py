import uuid
from datetime import date
from enum import Enum

from sqlalchemy import String, Date, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.patient_medication import PatientMedicationModel
    from app.models.appointment import Appointment
    from app.models.doctor_profile import DoctorProfile
    from app.models.doctor_patient_relationship import DoctorPatientRelationship
    from app.models.password_reset_request import PasswordResetRequestModel

class GenderEnum(str, Enum):
    male = "male"
    female = "female"
    other = "other"


class RoleEnum(str, Enum):
    admin = "admin"
    doctor = "doctor"
    patient = "patient"


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )

    national_id: Mapped[str] = mapped_column(String(11), unique=True, index=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)

    gender: Mapped[GenderEnum] = mapped_column(SAEnum(GenderEnum), nullable=False)
    role: Mapped[RoleEnum] = mapped_column(
        SAEnum(RoleEnum), default=RoleEnum.patient, nullable=False
    )

    # Relationships
    patient_medications: Mapped[list["PatientMedicationModel"]] = relationship(
        "PatientMedicationModel", back_populates="user"
    )
    doctor_appointments: Mapped[list["Appointment"]] = relationship(
        "Appointment",
        foreign_keys="Appointment.doctor_id",
        back_populates="doctor"
    )
    patient_appointments: Mapped[list["Appointment"]] = relationship(
        "Appointment",
        foreign_keys="Appointment.patient_id",
        back_populates="patient"
    )
    doctor_profile: Mapped["DoctorProfile | None"] = relationship(
        "DoctorProfile", back_populates="user", uselist=False
    )
    patient_relationships: Mapped[list["DoctorPatientRelationship"]] = relationship(
        "DoctorPatientRelationship",
        foreign_keys="DoctorPatientRelationship.doctor_id",
        back_populates="doctor"
    )
    doctor_relationships: Mapped[list["DoctorPatientRelationship"]] = relationship(
        "DoctorPatientRelationship",
        foreign_keys="DoctorPatientRelationship.patient_id",
        back_populates="patient"
    )
    password_reset_requests: Mapped[list["PasswordResetRequestModel"]] = relationship(
        "PasswordResetRequestModel", back_populates="user"
    )
