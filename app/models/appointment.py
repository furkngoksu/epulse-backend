import enum
import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import UserModel


class AppointmentStatusEnum(str, enum.Enum):
    FREE = "FREE"
    BOOKED = "BOOKED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    NO_SHOW = "NO_SHOW"


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    patient_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    appointment_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[AppointmentStatusEnum] = mapped_column(
        SAEnum(AppointmentStatusEnum), nullable=False, default=AppointmentStatusEnum.FREE
    )
    facility_name: Mapped[str] = mapped_column(String(200), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    doctor: Mapped["UserModel"] = relationship(
        "UserModel", foreign_keys=[doctor_id], back_populates="doctor_appointments"
    )
    patient: Mapped["UserModel | None"] = relationship(
        "UserModel", foreign_keys=[patient_id], back_populates="patient_appointments"
    )
