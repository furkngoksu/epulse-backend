import uuid
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.prescription import PrescriptionModel, Status


class PrescriptionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        skip: int = 0,
        limit: int = 50,
        status: Optional[Status] = None,
    ) -> list[PrescriptionModel]:
        q = self.db.query(PrescriptionModel)
        if status is not None:
            q = q.filter(PrescriptionModel.status == status)
        return q.offset(skip).limit(limit).all()

    def get_by_id(self, prescription_id: UUID) -> PrescriptionModel | None:
        return (
            self.db.query(PrescriptionModel)
            .filter(PrescriptionModel.id == prescription_id)
            .first()
        )

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

    def get_by_doctor_id(
        self,
        doctor_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
        status: Optional[Status] = None,
    ) -> list[PrescriptionModel]:
        q = self.db.query(PrescriptionModel).filter(PrescriptionModel.doctor_id == doctor_id)
        if status is not None:
            q = q.filter(PrescriptionModel.status == status)
        return q.offset(skip).limit(limit).all()

    def get_by_patient_id(
        self,
        patient_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
        status: Optional[Status] = None,
    ) -> list[PrescriptionModel]:
        q = self.db.query(PrescriptionModel).filter(PrescriptionModel.patient_id == patient_id)
        if status is not None:
            q = q.filter(PrescriptionModel.status == status)
        return q.offset(skip).limit(limit).all()
