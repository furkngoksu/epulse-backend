import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, DateTime, Enum as SQLEnum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from enum import Enum

if TYPE_CHECKING:
    from app.models.schedule import ScheduleModel

class DoseStatusEnum(str, Enum):
    PENDING = "PENDING"
    TAKEN = "TAKEN"
    MISSED = "MISSED"
    SKIPPED = "SKIPPED"

class ScheduleTimeModel(Base):
    __tablename__ = "schedule_times"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    schedule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("schedules.id"), nullable=False
    )

    dose_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    status: Mapped[DoseStatusEnum] = mapped_column(
        SQLEnum(DoseStatusEnum),
        default=DoseStatusEnum.PENDING,
        nullable=False
    )

    taken_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    
    skip_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)

    schedule: Mapped["ScheduleModel"] = relationship(
        "ScheduleModel", back_populates="schedule_times"
    )
