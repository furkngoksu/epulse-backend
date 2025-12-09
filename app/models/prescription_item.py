import uuid
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.medication import MedicationModel
    from app.models.prescription import PrescriptionModel

from app.db.base import Base


class PrescriptionItemModel(Base):
    __tablename__ = "prescription_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )

    prescription_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("prescriptions.id"), nullable=False
    )

    medication_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("medications.id"), nullable=False
    )

    dosage: Mapped[str] = mapped_column(String(100))
    duration: Mapped[int] = mapped_column(Integer)

    prescription: Mapped["PrescriptionModel"] = relationship(back_populates="items")
    medication: Mapped["MedicationModel"] = relationship(back_populates="prescription_items")
