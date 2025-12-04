import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base


class AppointmentStatusEnum(str, enum.Enum):
    FREE = "FREE"
    BOOKED = "BOOKED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    NO_SHOW = "NO_SHOW"


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    appointment_datetime = Column(DateTime, nullable=False)
    status = Column(Enum(AppointmentStatusEnum), nullable=False, default=AppointmentStatusEnum.FREE)
    facility_name = Column(String(200), nullable=False)
    notes = Column(Text, nullable=True)

    # Relationships
    doctor = relationship("User", foreign_keys=[doctor_id], backref="doctor_appointments")
    patient = relationship("User", foreign_keys=[patient_id], backref="patient_appointments")
