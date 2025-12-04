from sqlalchemy import Column, String, Integer, Text
from app.db.base import Base
from sqlalchemy.orm import relationship

class Medication(Base):
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    commercial_name = Column(String(200), nullable=False)
    active_ingredients = Column(String(500), nullable=False)
    dosage_form = Column(String(100), nullable=False)
    strength = Column(String(50), nullable=False)
    manufacturer = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Relationships
    patient_medications = relationship("PatientMedications", back_populates="medication")
