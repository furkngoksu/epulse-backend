import uuid
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.drug_interaction import DrugInteractionModel


class DrugInteractionRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> list[DrugInteractionModel]:
        return self.db.query(DrugInteractionModel).offset(skip).limit(limit).all()

    def get_by_id(self, interaction_id: uuid.UUID) -> DrugInteractionModel | None:
        return self.db.query(DrugInteractionModel).filter(DrugInteractionModel.id == interaction_id).first()

    def get_by_medication_ids(self, med_id_1: uuid.UUID, med_id_2: uuid.UUID) -> DrugInteractionModel | None:
        """
        Check if there's an interaction between two medications.
        Checks both directions since the interaction is bidirectional.
        """
        return (
            self.db.query(DrugInteractionModel)
            .filter(
                or_(
                    and_(
                        DrugInteractionModel.medication_id_1 == med_id_1,
                        DrugInteractionModel.medication_id_2 == med_id_2
                    ),
                    and_(
                        DrugInteractionModel.medication_id_1 == med_id_2,
                        DrugInteractionModel.medication_id_2 == med_id_1
                    )
                )
            )
            .first()
        )

    def get_interactions_for_medication(self, medication_id: uuid.UUID) -> list[DrugInteractionModel]:
        """Get all interactions involving a specific medication."""
        return (
            self.db.query(DrugInteractionModel)
            .filter(
                or_(
                    DrugInteractionModel.medication_id_1 == medication_id,
                    DrugInteractionModel.medication_id_2 == medication_id
                )
            )
            .all()
        )

    def create(self, interaction: DrugInteractionModel) -> DrugInteractionModel:
        self.db.add(interaction)
        self.db.commit()
        self.db.refresh(interaction)
        return interaction

    def update(self, interaction: DrugInteractionModel) -> DrugInteractionModel:
        self.db.commit()
        self.db.refresh(interaction)
        return interaction

    def delete(self, interaction: DrugInteractionModel) -> None:
        self.db.delete(interaction)
        self.db.commit()
