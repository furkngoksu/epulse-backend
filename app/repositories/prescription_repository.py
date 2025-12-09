import uuid
from app.models import PrescriptionModel
from sqlalchemy.orm import Session
from uuid import UUID

class PrescriptionRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 50) -> list[PrescriptionModel]:
        return self.db.query(PrescriptionModel).offset(skip).limit(limit).all()

    def get_by_id(self, prescription_id: UUID) -> PrescriptionModel | None:
        return self.db.query(PrescriptionModel).filter(PrescriptionModel.id == prescription_id).first()

    def create(self, prescription: PrescriptionModel) -> PrescriptionModel:
        self.db.add(prescription)
        self.db.commit()
        self.db.refresh(prescription)
        return prescription

    def update(self, prescription: PrescriptionModel) -> PrescriptionModel:
        self.db.commit()
        self.db.refresh(prescription)
        return prescription

    def delete(self, prescription: PrescriptionModel) -> None:
        self.db.delete(prescription)
        self.db.commit()

    def get_by_doctor_id(self, doctor_id: uuid.UUID, skip: int = 0, limit: int = 50) -> list[PrescriptionModel]:
        return self.db.query(PrescriptionModel).filter(PrescriptionModel.doctor_id == doctor_id).offset(skip).limit(limit).all()

    def get_by_patient_id(self, patient_id: uuid.UUID, skip: int = 0, limit: int = 50) -> list[PrescriptionModel]:
        return self.db.query(PrescriptionModel).filter(PrescriptionModel.patient_id == patient_id).offset(skip).limit(limit).all()