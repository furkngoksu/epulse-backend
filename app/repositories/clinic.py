import uuid
from sqlalchemy.orm import Session
from app.models.clinic import Clinic


class ClinicRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Clinic]:
        return self.db.query(Clinic).offset(skip).limit(limit).all()

    def get_by_id(self, clinic_id: uuid.UUID) -> Clinic | None:
        return self.db.query(Clinic).filter(Clinic.id == clinic_id).first()

    def get_by_hospital_id(self, hospital_id: uuid.UUID) -> list[Clinic]:
        return self.db.query(Clinic).filter(Clinic.hospital_id == hospital_id).all()

    def create(self, clinic: Clinic) -> Clinic:
        self.db.add(clinic)
        self.db.commit()
        self.db.refresh(clinic)
        return clinic

    def update(self, clinic: Clinic) -> Clinic:
        self.db.commit()
        self.db.refresh(clinic)
        return clinic

    def delete(self, clinic: Clinic) -> None:
        self.db.delete(clinic)
        self.db.commit()
