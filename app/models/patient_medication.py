from sqlalchemy import Boolean, Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.db.base import Base

class PatientMedication(Base):
    __tablename__ = "patient_medications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    medication_id = Column(Integer, ForeignKey("medications.id"), nullable=False)
    custom_name = Column(String(255), nullable=False)
    initial_stock = Column(Integer, nullable=False)
    current_stock = Column(Integer, nullable=False)
    stock_warning_threshold = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    user = relationship("User", back_populates="patient_medications", foreign_keys=[user_id])
    medication = relationship("Medication", back_populates="patient_medications", foreign_keys=[medication_id])
    dose_logs = relationship("DoseLog", back_populates="patient_medication", cascade="all, delete-orphan")