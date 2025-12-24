import uuid
from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import UserModel
    from app.models.medication import MedicationModel


class MedicationAliasModel(Base):
    __tablename__ = "medication_aliases"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    medication_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("medications.id"), nullable=False
    )
    alias_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Unique constraint: one alias per medication per user
    __table_args__ = (
        UniqueConstraint("user_id", "medication_id", name="uq_user_medication_alias"),
    )

    # Relationships
    user: Mapped["UserModel"] = relationship("UserModel", foreign_keys=[user_id])
    medication: Mapped["MedicationModel"] = relationship(
        "MedicationModel", foreign_keys=[medication_id]
    )
