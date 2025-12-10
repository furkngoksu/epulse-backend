from sqlalchemy import Boolean, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column

class PatientMedicationModel(Base):
    __tablename__ = "patient_medications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    medication_id: Mapped[int] = mapped_column(Integer, ForeignKey("medications.id"), nullable=False)
    custom_name: Mapped[str] = mapped_column(String(255), nullable=False)
    initial_stock: Mapped[int] = mapped_column(Integer, nullable=False)
    current_stock: Mapped[int] = mapped_column(Integer, nullable=False)
    stock_warning_threshold: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    user = relationship("UserModel", back_populates="patient_medications", foreign_keys=[user_id])
    medication = relationship("MedicationModel", back_populates="patient_medications", foreign_keys=[medication_id])

    # Primary relationships
    dose_logs = relationship("DoseLogModel", back_populates="patient_medication", cascade="all, delete-orphan")
    schedules = relationship("ScheduleModel", back_populates="patient_medication", cascade="all, delete-orphan")