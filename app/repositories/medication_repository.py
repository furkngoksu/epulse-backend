import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app.models.medication import MedicationModel


class MedicationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        q: Optional[str] = None,
    ) -> list[MedicationModel]:
        query = self.db.query(MedicationModel)

        if q:
            query = query.filter(MedicationModel.commercial_name.ilike(f"%{q}%"))

        return query.offset(skip).limit(limit).all()

    def get_by_id(self, medication_id: uuid.UUID) -> MedicationModel | None:
        return (
            self.db.query(MedicationModel)
            .filter(MedicationModel.id == medication_id)
            .first()
        )

    def create(self, medication: MedicationModel) -> MedicationModel:
        self.db.add(medication)
        self.db.commit()
        self.db.refresh(medication)
        return medication

    def update(self, medication: MedicationModel) -> MedicationModel:
        self.db.commit()
        self.db.refresh(medication)
        return medication

    def delete(self, medication: MedicationModel) -> None:
        self.db.delete(medication)
        self.db.commit()
