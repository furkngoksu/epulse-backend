import uuid
from sqlalchemy.orm import Session
from app.models.hospital import Hospital


class HospitalRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Hospital]:
        return self.db.query(Hospital).offset(skip).limit(limit).all()

    def get_by_id(self, hospital_id: uuid.UUID) -> Hospital | None:
        return self.db.query(Hospital).filter(Hospital.id == hospital_id).first()

    def create(self, hospital: Hospital) -> Hospital:
        self.db.add(hospital)
        self.db.commit()
        self.db.refresh(hospital)
        return hospital

    def update(self, hospital: Hospital) -> Hospital:
        self.db.commit()
        self.db.refresh(hospital)
        return hospital

    def delete(self, hospital: Hospital) -> None:
        self.db.delete(hospital)
        self.db.commit()
