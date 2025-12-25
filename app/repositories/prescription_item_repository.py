import uuid
from sqlalchemy.orm import Session
from app.models import PrescriptionItemModel


class PrescriptionItemRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 50) -> list[PrescriptionItemModel]:
        return self.db.query(PrescriptionItemModel).offset(skip).limit(limit).all()

    def get_by_id(
        self, prescription_item_id: uuid.UUID
    ) -> PrescriptionItemModel | None:
        return (
            self.db.query(PrescriptionItemModel)
            .filter(PrescriptionItemModel.id == prescription_item_id)
            .first()
        )

    def get_by_prescription_id(
        self,
        prescription_id: uuid.UUID,
        skip: int = 0,
        limit: int = 200,
    ) -> list[PrescriptionItemModel]:
        return (
            self.db.query(PrescriptionItemModel)
            .filter(PrescriptionItemModel.prescription_id == prescription_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, prescription_item: PrescriptionItemModel) -> PrescriptionItemModel:
        self.db.add(prescription_item)
        self.db.commit()
        self.db.refresh(prescription_item)
        return prescription_item

    def create_many(
        self, items: list[PrescriptionItemModel]
    ) -> list[PrescriptionItemModel]:
        if not items:
            return []
        self.db.add_all(items)
        self.db.commit()
        for it in items:
            self.db.refresh(it)
        return items

    def update(self, prescription_item: PrescriptionItemModel) -> PrescriptionItemModel:
        self.db.commit()
        self.db.refresh(prescription_item)
        return prescription_item

    def delete(self, prescription_item: PrescriptionItemModel) -> None:
        self.db.delete(prescription_item)
        self.db.commit()
