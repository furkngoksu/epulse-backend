from typing import TYPE_CHECKING
import uuid
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.prescription_item import PrescriptionItemModel

class MedicationModel(Base):
    __tablename__ = "medications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )

    commercial_name: Mapped[str] = mapped_column(String(200), nullable=False)
    active_ingredients: Mapped[str] = mapped_column(String(500), nullable=False)
    dosage_form: Mapped[str] = mapped_column(String(100), nullable=False)
    strength: Mapped[str] = mapped_column(String(50), nullable=False)
    manufacturer: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    prescription_items: Mapped[list["PrescriptionItemModel"]] = relationship(
        back_populates="medication"
    )
