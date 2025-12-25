import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import UserModel
    from app.models.clinic import Clinic


class DoctorProfile(Base):
    __tablename__ = "doctor_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True
    )
    clinic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clinics.id"), nullable=False
    )
    specialty: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationships
    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="doctor_profile"
    )
    clinic: Mapped["Clinic"] = relationship("Clinic", back_populates="doctor_profiles")
