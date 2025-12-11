from sqlalchemy import Boolean, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import UserModel
    from app.models.medication import MedicationModel
    from app.models.dose_log import DoseLogModel
    from app.models.schedule import ScheduleModel

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
    user : Mapped["UserModel"] = relationship("UserModel", back_populates="patient_medications", foreign_keys=[user_id])
    medication : Mapped["MedicationModel"] = relationship("MedicationModel", back_populates="patient_medications", foreign_keys=[medication_id])

    # Primary relationships
    dose_logs : Mapped[list["DoseLogModel"]] = relationship("DoseLogModel", back_populates="patient_medication", cascade="all, delete-orphan")
    schedules : Mapped[list["ScheduleModel"]] = relationship("ScheduleModel", back_populates="patient_medication", cascade="all, delete-orphan")