import uuid
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.doctor_patient_relationship import DoctorPatientRelationship


class DoctorPatientRelationshipRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> list[DoctorPatientRelationship]:
        return self.db.query(DoctorPatientRelationship).offset(skip).limit(limit).all()

    def get_by_id(self, relationship_id: uuid.UUID) -> DoctorPatientRelationship | None:
        return (
            self.db.query(DoctorPatientRelationship)
            .filter(DoctorPatientRelationship.id == relationship_id)
            .first()
        )

    def get_by_doctor_and_patient(
        self, doctor_id: uuid.UUID, patient_id: uuid.UUID
    ) -> DoctorPatientRelationship | None:
        """Check if a relationship already exists between a doctor and patient."""
        return (
            self.db.query(DoctorPatientRelationship)
            .filter(
                and_(
                    DoctorPatientRelationship.doctor_id == doctor_id,
                    DoctorPatientRelationship.patient_id == patient_id,
                )
            )
            .first()
        )

    def get_patients_for_doctor(
        self, doctor_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[DoctorPatientRelationship]:
        """Get all patients for a specific doctor."""
        return (
            self.db.query(DoctorPatientRelationship)
            .filter(DoctorPatientRelationship.doctor_id == doctor_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_doctors_for_patient(
        self, patient_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[DoctorPatientRelationship]:
        """Get all doctors for a specific patient."""
        return (
            self.db.query(DoctorPatientRelationship)
            .filter(DoctorPatientRelationship.patient_id == patient_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(
        self, relationship: DoctorPatientRelationship
    ) -> DoctorPatientRelationship:
        self.db.add(relationship)
        self.db.commit()
        self.db.refresh(relationship)
        return relationship

    def delete(self, relationship: DoctorPatientRelationship) -> None:
        self.db.delete(relationship)
        self.db.commit()
