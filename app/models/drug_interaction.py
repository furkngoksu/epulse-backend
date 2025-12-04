from sqlalchemy import Column, Integer, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class SeverityEnum(str, enum.Enum):
    MINOR = "MINOR"
    MODERATE = "MODERATE"
    SEVERE = "SEVERE"


class DrugInteraction(Base):
    __tablename__ = "drug_interactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    medication_id_1 = Column(Integer, ForeignKey("medications.id"), nullable=False)
    medication_id_2 = Column(Integer, ForeignKey("medications.id"), nullable=False)
    severity = Column(Enum(SeverityEnum), nullable=False)
    interaction_description = Column(Text, nullable=True)

    # Relationships
    medication_1 = relationship("Medication", foreign_keys=[medication_id_1])
    medication_2 = relationship("Medication", foreign_keys=[medication_id_2])
