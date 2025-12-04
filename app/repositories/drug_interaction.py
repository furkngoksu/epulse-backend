from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.drug_interaction import DrugInteraction


class DrugInteractionRepository:

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[DrugInteraction]:
        return db.query(DrugInteraction).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, interaction_id: int) -> DrugInteraction | None:
        return db.query(DrugInteraction).filter(DrugInteraction.id == interaction_id).first()

    @staticmethod
    def get_by_medication_ids(db: Session, med_id_1: int, med_id_2: int) -> DrugInteraction | None:
        """
        Check if there's an interaction between two medications.
        Checks both directions since the interaction is bidirectional.
        """
        return (
            db.query(DrugInteraction)
            .filter(
                or_(
                    and_(
                        DrugInteraction.medication_id_1 == med_id_1,
                        DrugInteraction.medication_id_2 == med_id_2
                    ),
                    and_(
                        DrugInteraction.medication_id_1 == med_id_2,
                        DrugInteraction.medication_id_2 == med_id_1
                    )
                )
            )
            .first()
        )

    @staticmethod
    def get_interactions_for_medication(db: Session, medication_id: int) -> list[DrugInteraction]:
        """Get all interactions involving a specific medication."""
        return (
            db.query(DrugInteraction)
            .filter(
                or_(
                    DrugInteraction.medication_id_1 == medication_id,
                    DrugInteraction.medication_id_2 == medication_id
                )
            )
            .all()
        )

    @staticmethod
    def create(db: Session, interaction: DrugInteraction) -> DrugInteraction:
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        return interaction

    @staticmethod
    def update(db: Session, interaction: DrugInteraction) -> DrugInteraction:
        db.commit()
        db.refresh(interaction)
        return interaction

    @staticmethod
    def delete(db: Session, interaction: DrugInteraction) -> None:
        db.delete(interaction)
        db.commit()
