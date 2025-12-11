from sqlalchemy import String, Integer, Text
from app.db.base import Base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.prescription_item import PrescriptionItemModel

class MedicationModel(Base):
    __tablename__ = "medications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    commercial_name: Mapped[str] = mapped_column(String(200), nullable=False)
    active_ingredients: Mapped[str] = mapped_column(String(500), nullable=False)
    dosage_form: Mapped[str] = mapped_column(String(100), nullable=False)
    strength: Mapped[str] = mapped_column(String(50), nullable=False)
    manufacturer: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    prescription_items: Mapped[list["PrescriptionItemModel"]] = relationship("PrescriptionItemModel", back_populates="medication")
