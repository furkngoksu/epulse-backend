from app.db.base import Base
from sqlalchemy import ForeignKey, Integer, Time
from sqlalchemy.orm import relationship, Mapped, mapped_column

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.schedule import ScheduleModel

class ScheduleTimeModel(Base):
    __tablename__ = "schedule_times"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    schedule_id: Mapped[int] = mapped_column(Integer, ForeignKey("schedules.id"), nullable=False)
    dose_time: Mapped[Time] = mapped_column(Time, nullable=False)

    # Relationships
    schedule: Mapped["ScheduleModel"] = relationship("ScheduleModel", back_populates="schedule_times")