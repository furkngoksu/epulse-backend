from sqlalchemy.orm import Session
from app.models.hospital import Hospital


class HospitalRepository:

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Hospital]:
        return db.query(Hospital).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, hospital_id: int) -> Hospital | None:
        return db.query(Hospital).filter(Hospital.id == hospital_id).first()

    @staticmethod
    def create(db: Session, hospital: Hospital) -> Hospital:
        db.add(hospital)
        db.commit()
        db.refresh(hospital)
        return hospital

    @staticmethod
    def update(db: Session, hospital: Hospital) -> Hospital:
        db.commit()
        db.refresh(hospital)
        return hospital

    @staticmethod
    def delete(db: Session, hospital: Hospital) -> None:
        db.delete(hospital)
        db.commit()
