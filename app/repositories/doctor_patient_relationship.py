from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.doctor_patient_relationship import DoctorPatientRelationship


class DoctorPatientRelationshipRepository:

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[DoctorPatientRelationship]:
        return db.query(DoctorPatientRelationship).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, relationship_id: int) -> DoctorPatientRelationship | None:
        return db.query(DoctorPatientRelationship).filter(
            DoctorPatientRelationship.id == relationship_id
        ).first()

    @staticmethod
    def get_by_doctor_and_patient(
        db: Session, doctor_id: int, patient_id: int
    ) -> DoctorPatientRelationship | None:
        """Check if a relationship already exists between a doctor and patient."""
        return db.query(DoctorPatientRelationship).filter(
            and_(
                DoctorPatientRelationship.doctor_id == doctor_id,
                DoctorPatientRelationship.patient_id == patient_id
            )
        ).first()

    @staticmethod
    def get_patients_for_doctor(db: Session, doctor_id: int, skip: int = 0, limit: int = 100) -> list[DoctorPatientRelationship]:
        """Get all patients for a specific doctor."""
        return db.query(DoctorPatientRelationship).filter(
            DoctorPatientRelationship.doctor_id == doctor_id
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_doctors_for_patient(db: Session, patient_id: int, skip: int = 0, limit: int = 100) -> list[DoctorPatientRelationship]:
        """Get all doctors for a specific patient."""
        return db.query(DoctorPatientRelationship).filter(
            DoctorPatientRelationship.patient_id == patient_id
        ).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, relationship: DoctorPatientRelationship) -> DoctorPatientRelationship:
        db.add(relationship)
        db.commit()
        db.refresh(relationship)
        return relationship

    @staticmethod
    def delete(db: Session, relationship: DoctorPatientRelationship) -> None:
        db.delete(relationship)
        db.commit()
