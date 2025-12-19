from enum import Enum
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import String, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.prescription_item import PrescriptionItemModel

class Status(str, Enum):
    active = "active"
    inactive = "inactive"

class PrescriptionModel(Base):
    __tablename__ = "prescriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )

    doctor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    status: Mapped[Status] = mapped_column(
        SAEnum(Status), nullable=False, default=Status.inactive
    )

    items: Mapped[list["PrescriptionItemModel"]] = relationship(
        back_populates="prescription", cascade="all, delete-orphan"
    )
