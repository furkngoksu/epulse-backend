import uuid
from sqlalchemy import Enum, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
import enum
from sqlalchemy import UUID

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.patient_medication import PatientMedicationModel

class  DoseStatusEnum(str, enum.Enum):
    TAKEN = "TAKEN"
    MISSED = "MISSED"
    SKIPPED = "SKIPPED"

class DoseLogModel(Base):
    __tablename__ = "dose_logs"

    id : Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4, index=True)
    patient_medication_id : Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("patient_medications.id"), nullable=False)
    scheduled_time : Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    taken_time : Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status : Mapped[DoseStatusEnum] = mapped_column(Enum(DoseStatusEnum), nullable=False)
    skip_reason : Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    patient_medication : Mapped["PatientMedicationModel"] = relationship("PatientMedicationModel", back_populates="dose_logs", foreign_keys=[patient_medication_id])