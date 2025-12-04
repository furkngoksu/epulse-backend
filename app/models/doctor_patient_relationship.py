from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class DoctorPatientRelationship(Base):
    __tablename__ = "doctor_patient_relationships"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    doctor = relationship("User", foreign_keys=[doctor_id], backref="patient_relationships")
    patient = relationship("User", foreign_keys=[patient_id], backref="doctor_relationships")
