import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.patient_medication import PatientMedicationModel
    from app.models.schedule_time import ScheduleTimeModel


class ScheduleModel(Base):
    __tablename__ = "schedules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    patient_medication_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patient_medications.id"), nullable=False
    )
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    specific_days: Mapped[Any | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    patient_medication: Mapped["PatientMedicationModel"] = relationship(
        "PatientMedicationModel", back_populates="schedules"
    )
    schedule_times: Mapped[list["ScheduleTimeModel"]] = relationship(
        "ScheduleTimeModel", back_populates="schedule", cascade="all, delete-orphan"
    )
