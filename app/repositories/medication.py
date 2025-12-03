from sqlalchemy.orm import Session
from app.models.medication import Medication


class MedicationRepository:

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Medication]:
        return db.query(Medication).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, medication_id: int) -> Medication | None:
        return db.query(Medication).filter(Medication.id == medication_id).first()

    @staticmethod
    def search_by_name(db: Session, name: str, skip: int = 0, limit: int = 100) -> list[Medication]:
        return (
            db.query(Medication)
            .filter(Medication.commercial_name.ilike(f"%{name}%"))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def create(db: Session, medication: Medication) -> Medication:
        db.add(medication)
        db.commit()
        db.refresh(medication)
        return medication

    @staticmethod
    def update(db: Session, medication: Medication) -> Medication:
        db.commit()
        db.refresh(medication)
        return medication

    @staticmethod
    def delete(db: Session, medication: Medication) -> None:
        db.delete(medication)
        db.commit()
