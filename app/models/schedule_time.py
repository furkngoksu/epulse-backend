import uuid
from datetime import time
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.schedule import ScheduleModel


class ScheduleTimeModel(Base):
    __tablename__ = "schedule_times"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    schedule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("schedules.id"), nullable=False
    )
    dose_time: Mapped[time] = mapped_column(Time, nullable=False)

    # Relationships
    schedule: Mapped["ScheduleModel"] = relationship(
        "ScheduleModel", back_populates="schedule_times"
    )