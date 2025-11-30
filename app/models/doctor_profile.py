from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base


class DoctorProfile(Base):
    __tablename__ = "doctor_profiles"

    id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    hospital_id = Column(UUID(as_uuid=True), ForeignKey("hospitals.id"), nullable=False)
    specialty = Column(String(100), nullable=False)

    # Relationships
    user = relationship("User", backref="doctor_profile")
    hospital = relationship("Hospital", backref="doctor_profiles")
