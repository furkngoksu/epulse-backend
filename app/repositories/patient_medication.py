from app.models.patient_medication import PatientMedication
from sqlalchemy.orm import Session


class PatientMedicationRepository:

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[PatientMedication]:
        return db.query(PatientMedication).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_id(db: Session, patient_medication_id: int) -> PatientMedication | None:
        return db.query(PatientMedication).filter(PatientMedication.id == patient_medication_id).first()
    
    @staticmethod
    def get_by_user_id(db: Session, user_id: int) -> list[PatientMedication]:
        return db.query(PatientMedication).filter(PatientMedication.user_id == user_id).all()

    @staticmethod
    def create(db: Session, patient_medication: PatientMedication) -> PatientMedication:
        db.add(patient_medication)
        db.commit()
        db.refresh(patient_medication)
        return patient_medication
    
    @staticmethod
    def update(db: Session, patient_medication: PatientMedication) -> PatientMedication:
        db.commit()
        db.refresh(patient_medication)
        return patient_medication
    
    @staticmethod
    def delete(db: Session, patient_medication: PatientMedication) -> None:
        db.delete(patient_medication)
        db.commit()
    
