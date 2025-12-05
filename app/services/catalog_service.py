from sqlalchemy.orm import Session

from app.models.medication import Medication
from app.models.drug_interaction import DrugInteraction
<<<<<<< HEAD:app/services/drug_interaction.py
from app.repositories.drug_interaction import DrugInteractionRepository
from app.repositories.medication_repository import MedicationRepository
=======
from app.repositories.medication import MedicationRepository
from app.repositories.drug_interaction import DrugInteractionRepository
from app.schemas.medication import MedicationCreate, MedicationUpdate
>>>>>>> f1dddcd (rebase from main):app/services/catalog_service.py
from app.schemas.drug_interaction import DrugInteractionCreate, DrugInteractionUpdate
from app.exceptions.exceptions import NotFoundException, BadRequestException, ConflictException


class CatalogService:
    """
    Consolidated service for managing medications and drug interactions.
    """

    # ==================== Medication Methods ====================

    @staticmethod
    def get_all_medications(db: Session, skip: int = 0, limit: int = 100) -> list[Medication]:
        return MedicationRepository.get_all(db, skip=skip, limit=limit)

    @staticmethod
    def get_medication_by_id(db: Session, medication_id: int) -> Medication:
        medication = MedicationRepository.get_by_id(db, medication_id)
        if not medication:
            raise NotFoundException("Medication not found")
        return medication

    @staticmethod
    def search_medications(db: Session, name: str, skip: int = 0, limit: int = 100) -> list[Medication]:
        return MedicationRepository.search_by_name(db, name, skip=skip, limit=limit)

    @staticmethod
    def create_medication(db: Session, data: MedicationCreate) -> Medication:
        medication = Medication(
            commercial_name=data.commercial_name,
            active_ingredients=data.active_ingredients,
            dosage_form=data.dosage_form,
            strength=data.strength,
            manufacturer=data.manufacturer,
            description=data.description
        )
        return MedicationRepository.create(db, medication)

    @staticmethod
    def update_medication(db: Session, medication_id: int, data: MedicationUpdate) -> Medication:
        medication = MedicationRepository.get_by_id(db, medication_id)
        if not medication:
            raise NotFoundException("Medication not found")

        # Update only provided fields
        if data.commercial_name is not None:
            medication.commercial_name = data.commercial_name
        if data.active_ingredients is not None:
            medication.active_ingredients = data.active_ingredients
        if data.dosage_form is not None:
            medication.dosage_form = data.dosage_form
        if data.strength is not None:
            medication.strength = data.strength
        if data.manufacturer is not None:
            medication.manufacturer = data.manufacturer
        if data.description is not None:
            medication.description = data.description

        return MedicationRepository.update(db, medication)

    @staticmethod
    def delete_medication(db: Session, medication_id: int) -> None:
        medication = MedicationRepository.get_by_id(db, medication_id)
        if not medication:
            raise NotFoundException("Medication not found")
        MedicationRepository.delete(db, medication)

    # ==================== Drug Interaction Methods ====================

    @staticmethod
    def get_all_interactions(db: Session, skip: int = 0, limit: int = 100) -> list[DrugInteraction]:
        return DrugInteractionRepository.get_all(db, skip=skip, limit=limit)

    @staticmethod
    def get_interaction_by_id(db: Session, interaction_id: int) -> DrugInteraction:
        interaction = DrugInteractionRepository.get_by_id(db, interaction_id)
        if not interaction:
            raise NotFoundException("Drug interaction not found")
        return interaction

    @staticmethod
    def check_drug_interaction(db: Session, med_id_1: int, med_id_2: int) -> DrugInteraction | None:
        """Check if there's an interaction between two medications."""
        if med_id_1 == med_id_2:
            raise BadRequestException("Cannot check interaction of a medication with itself")

        return DrugInteractionRepository.get_by_medication_ids(db, med_id_1, med_id_2)

    @staticmethod
    def get_medication_interactions(db: Session, medication_id: int) -> list[DrugInteraction]:
        """Get all interactions for a specific medication."""
        # Verify medication exists
        medication = MedicationRepository.get_by_id(db, medication_id)
        if not medication:
            raise NotFoundException("Medication not found")

        return DrugInteractionRepository.get_interactions_for_medication(db, medication_id)

    @staticmethod
    def create_interaction(db: Session, data: DrugInteractionCreate) -> DrugInteraction:
        # Validate medications exist
        med_1 = MedicationRepository.get_by_id(db, data.medication_id_1)
        if not med_1:
            raise NotFoundException(f"Medication with id {data.medication_id_1} not found")

        med_2 = MedicationRepository.get_by_id(db, data.medication_id_2)
        if not med_2:
            raise NotFoundException(f"Medication with id {data.medication_id_2} not found")

        # Validate not same medication
        if data.medication_id_1 == data.medication_id_2:
            raise BadRequestException("Cannot create interaction for a medication with itself")

        # Check if interaction already exists
        existing = DrugInteractionRepository.get_by_medication_ids(
            db, data.medication_id_1, data.medication_id_2
        )
        if existing:
            raise ConflictException("Interaction between these medications already exists")

        interaction = DrugInteraction(
            medication_id_1=data.medication_id_1,
            medication_id_2=data.medication_id_2,
            severity=data.severity,
            interaction_description=data.interaction_description
        )
        return DrugInteractionRepository.create(db, interaction)

    @staticmethod
    def update_interaction(db: Session, interaction_id: int, data: DrugInteractionUpdate) -> DrugInteraction:
        interaction = DrugInteractionRepository.get_by_id(db, interaction_id)
        if not interaction:
            raise NotFoundException("Drug interaction not found")

        # Update only provided fields
        if data.medication_id_1 is not None:
            # Verify medication exists
            med = MedicationRepository.get_by_id(db, data.medication_id_1)
            if not med:
                raise NotFoundException(f"Medication with id {data.medication_id_1} not found")
            interaction.medication_id_1 = data.medication_id_1

        if data.medication_id_2 is not None:
            # Verify medication exists
            med = MedicationRepository.get_by_id(db, data.medication_id_2)
            if not med:
                raise NotFoundException(f"Medication with id {data.medication_id_2} not found")
            interaction.medication_id_2 = data.medication_id_2

        # Validate not same medication after update
        if interaction.medication_id_1 == interaction.medication_id_2:
            raise BadRequestException("Cannot create interaction for a medication with itself")

        if data.severity is not None:
            interaction.severity = data.severity

        if data.interaction_description is not None:
            interaction.interaction_description = data.interaction_description

        return DrugInteractionRepository.update(db, interaction)

    @staticmethod
    def delete_interaction(db: Session, interaction_id: int) -> None:
        interaction = DrugInteractionRepository.get_by_id(db, interaction_id)
        if not interaction:
            raise NotFoundException("Drug interaction not found")
        DrugInteractionRepository.delete(db, interaction)
