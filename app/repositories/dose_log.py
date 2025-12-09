from sqlalchemy.orm import Session
from app.models.dose_log import DoseLog

class DoseLogRepository:

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[DoseLog]:
        return db.query(DoseLog).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, dose_log_id: int) -> DoseLog | None:
        return db.query(DoseLog).filter(DoseLog.id == dose_log_id).first()

    @staticmethod
    def get_by_patient_id(db: Session, patient_id: int) -> list[DoseLog]:
        return db.query(DoseLog).filter(DoseLog.patient_id == patient_id).all()

    @staticmethod
    def create(db: Session, dose_log: DoseLog) -> DoseLog:
        db.add(dose_log)
        db.commit()
        db.refresh(dose_log)
        return dose_log

    @staticmethod
    def update(db: Session, dose_log: DoseLog) -> DoseLog:
        db.commit()
        db.refresh(dose_log)
        return dose_log

    @staticmethod
    def delete(db: Session, dose_log: DoseLog) -> None:
        db.delete(dose_log)
        db.commit()
