import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.hospital import Hospital
    from app.models.doctor_profile import DoctorProfile


class Clinic(Base):
    __tablename__ = "clinics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    hospital_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hospitals.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationships
    hospital: Mapped["Hospital"] = relationship("Hospital", back_populates="clinics")
    doctor_profiles: Mapped[list["DoctorProfile"]] = relationship(
        "DoctorProfile", back_populates="clinic"
    )
