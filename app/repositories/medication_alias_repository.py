import uuid
from sqlalchemy.orm import Session

from app.models.medication_alias import MedicationAliasModel


class MedicationAliasRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, alias: MedicationAliasModel) -> MedicationAliasModel:
        self.db.add(alias)
        self.db.commit()
        self.db.refresh(alias)
        return alias

    def get_all_by_user(self, user_id: uuid.UUID) -> list[MedicationAliasModel]:
        return (
            self.db.query(MedicationAliasModel)
            .filter(MedicationAliasModel.user_id == user_id)
            .all()
        )

    def get_by_id(self, alias_id: uuid.UUID) -> MedicationAliasModel | None:
        return (
            self.db.query(MedicationAliasModel)
            .filter(MedicationAliasModel.id == alias_id)
            .first()
        )

    def get_by_id_for_user(
        self, alias_id: uuid.UUID, user_id: uuid.UUID
    ) -> MedicationAliasModel | None:
        return (
            self.db.query(MedicationAliasModel)
            .filter(MedicationAliasModel.id == alias_id)
            .filter(MedicationAliasModel.user_id == user_id)
            .first()
        )

    def get_by_user_and_medication(
        self, user_id: uuid.UUID, medication_id: uuid.UUID
    ) -> MedicationAliasModel | None:
        return (
            self.db.query(MedicationAliasModel)
            .filter(MedicationAliasModel.user_id == user_id)
            .filter(MedicationAliasModel.medication_id == medication_id)
            .first()
        )

    def update(self, alias: MedicationAliasModel) -> MedicationAliasModel:
        obj = self.db.merge(alias)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, alias: MedicationAliasModel) -> None:
        self.db.delete(alias)
        self.db.commit()
