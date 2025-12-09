from sqlalchemy.orm import Session
from app.models.medication import MedicationModel


class MedicationRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> list[MedicationModel]:
        return self.db.query(MedicationModel).offset(skip).limit(limit).all()

    def get_by_id(self, medication_id: int) -> MedicationModel | None:
        return self.db.query(MedicationModel).filter(MedicationModel.id == medication_id).first()

    def search_by_name(self, name: str, skip: int = 0, limit: int = 100) -> list[MedicationModel]:
        return (
            self.db.query(MedicationModel)
            .filter(MedicationModel.commercial_name.ilike(f"%{name}%"))
            .offset(skip)
            .limit(limit)
            .all()
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
        self.db.delete(medication)
        self.db.commit()
