import enum
import uuid
from sqlalchemy import ForeignKey, Text, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.medication import MedicationModel


class SeverityEnum(str, enum.Enum):
    minor = "minor"
    moderate = "moderate"
    severe = "severe"


class DrugInteraction(Base):
    __tablename__ = "drug_interactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    medication_id_1: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("medications.id"), nullable=False
    )
    medication_id_2: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("medications.id"), nullable=False
    )
    severity: Mapped[SeverityEnum] = mapped_column(SAEnum(SeverityEnum), nullable=False)
    interaction_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    medication_1: Mapped["MedicationModel"] = relationship(
        "MedicationModel", foreign_keys=[medication_id_1]
    )
    medication_2: Mapped["MedicationModel"] = relationship(
        "MedicationModel", foreign_keys=[medication_id_2]
    )
