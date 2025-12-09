import uuid
from sqlalchemy.orm import Session
from app.models import PrescriptionItemModel
import uuid

class PrescriptionItemRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 50) -> list[PrescriptionItemModel]:
        return self.db.query(PrescriptionItemModel).offset(skip).limit(limit).all()

    def get_by_id(self, prescription_item_id: uuid.UUID) -> PrescriptionItemModel | None:
        return self.db.query(PrescriptionItemModel).filter(PrescriptionItemModel.id == prescription_item_id).first()

    def create(self, prescription_item: PrescriptionItemModel) -> PrescriptionItemModel:
        self.db.add(prescription_item)
        self.db.commit()
        self.db.refresh(prescription_item)
        return prescription_item

    def update(self, prescription_item: PrescriptionItemModel) -> PrescriptionItemModel:
        self.db.commit()
        self.db.refresh(prescription_item)
        return prescription_item

    def delete(self, prescription_item: PrescriptionItemModel) -> None:
        self.db.delete(prescription_item)
        self.db.commit()
