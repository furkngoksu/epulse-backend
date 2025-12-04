from sqlalchemy import Column, Enum, Integer, ForeignKey, DateTime, Boolean, String
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum

class  DoseStatusEnum(str, enum.Enum):
    taken = "taken"
    missed = "missed"
    skipped = "skipped"

class DoseLog(Base):
    __tablename__ = "dose_logs"

    id = Column(Integer, primary_key=True, index=True)
    patient_medication_id = Column(Integer, ForeignKey("patient_medications.id"), nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    taken_time = Column(DateTime, nullable=True)
    status = Column(Enum(DoseStatusEnum), nullable=False)
    skip_reason = Column(String(500), nullable=True)

    # Relationships
    patient_medication = relationship("PatientMedication", back_populates="dose_logs", foreign_keys=[patient_medication_id])