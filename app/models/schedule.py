from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
import uuid
from datetime import datetime
from sqlalchemy.orm import relationship
from app.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.patient_medication import PatientMedicationModel
    from app.models.schedule_time import ScheduleTimeModel

class ScheduleModel(Base):
    __tablename__ = "schedules"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    patient_medication_id: Mapped[uuid.UUID] = mapped_column()
    start_date: Mapped[datetime] = mapped_column()
    end_date: Mapped[datetime] = mapped_column()

    specific_days: Mapped[JSONB] = mapped_column(JSONB, nullable=True)

    patient_medication: Mapped["PatientMedicationModel"] = relationship("PatientMedicationModel", back_populates="schedules")
    schedule_times: Mapped[list["ScheduleTimeModel"]] = relationship("ScheduleTimeModel", back_populates="schedule", cascade="all, delete-orphan")
