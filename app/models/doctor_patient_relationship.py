import uuid
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import UserModel


class DoctorPatientRelationship(Base):
    __tablename__ = "doctor_patient_relationships"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    # Relationships
    doctor: Mapped["UserModel"] = relationship(
        "UserModel", foreign_keys=[doctor_id], back_populates="patient_relationships"
    )
    patient: Mapped["UserModel"] = relationship(
        "UserModel", foreign_keys=[patient_id], back_populates="doctor_relationships"
    )
