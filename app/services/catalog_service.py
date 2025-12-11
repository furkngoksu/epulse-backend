import uuid
from app.models.medication import MedicationModel as Medication
from app.models.drug_interaction import DrugInteraction
from app.repositories.drug_interaction import DrugInteractionRepository
from app.repositories.medication_repository import MedicationRepository
from app.schemas.medication import MedicationCreate, MedicationUpdate
from app.schemas.drug_interaction import DrugInteractionCreate, DrugInteractionUpdate
from app.exceptions.exceptions import NotFoundException, BadRequestException, ConflictException


class CatalogService:
    """
    Consolidated service for managing medications and drug interactions.
    """

    def __init__(
        self,
        medication_repository: MedicationRepository,
        drug_interaction_repository: DrugInteractionRepository
    ):
        self.medication_repository = medication_repository
        self.drug_interaction_repository = drug_interaction_repository

    # ==================== Medication Methods ====================

    def get_all_medications(self, skip: int = 0, limit: int = 100) -> list[Medication]:
        return self.medication_repository.get_all(skip=skip, limit=limit)

    def get_medication_by_id(self, medication_id: uuid.UUID) -> Medication:
        medication = self.medication_repository.get_by_id(medication_id)
        if not medication:
            raise NotFoundException("Medication not found")
        return medication

    def search_medications(self, name: str, skip: int = 0, limit: int = 100) -> list[Medication]:
        return self.medication_repository.search_by_name(name, skip=skip, limit=limit)

    def create_medication(self, data: MedicationCreate) -> Medication:
        medication = Medication(
            commercial_name=data.commercial_name,
            active_ingredients=data.active_ingredients,
            dosage_form=data.dosage_form,
            strength=data.strength,
            manufacturer=data.manufacturer,
            description=data.description
        )
        return self.medication_repository.create(medication)

    def update_medication(self, medication_id: uuid.UUID, data: MedicationUpdate) -> Medication:
        medication = self.medication_repository.get_by_id(medication_id)
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

        return self.medication_repository.update(medication)

    def delete_medication(self, medication_id: uuid.UUID) -> None:
        medication = self.medication_repository.get_by_id(medication_id)
        if not medication:
            raise NotFoundException("Medication not found")
        self.medication_repository.delete(medication)

    # ==================== Drug Interaction Methods ====================

    def get_all_interactions(self, skip: int = 0, limit: int = 100) -> list[DrugInteraction]:
        return self.drug_interaction_repository.get_all(skip=skip, limit=limit)

    def get_interaction_by_id(self, interaction_id: uuid.UUID) -> DrugInteraction:
        interaction = self.drug_interaction_repository.get_by_id(interaction_id)
        if not interaction:
            raise NotFoundException("Drug interaction not found")
        return interaction

    def check_drug_interaction(self, med_id_1: uuid.UUID, med_id_2: uuid.UUID) -> DrugInteraction | None:
        """Check if there's an interaction between two medications."""
        if med_id_1 == med_id_2:
            raise BadRequestException("Cannot check interaction of a medication with itself")

        return self.drug_interaction_repository.get_by_medication_ids(med_id_1, med_id_2)

    def get_medication_interactions(self, medication_id: uuid.UUID) -> list[DrugInteraction]:
        """Get all interactions for a specific medication."""
        # Verify medication exists
        medication = self.medication_repository.get_by_id(medication_id)
        if not medication:
            raise NotFoundException("Medication not found")

        return self.drug_interaction_repository.get_interactions_for_medication(medication_id)

    def create_interaction(self, data: DrugInteractionCreate) -> DrugInteraction:
        # Validate medications exist
        med_1 = self.medication_repository.get_by_id(data.medication_id_1)
        if not med_1:
            raise NotFoundException(f"Medication with id {data.medication_id_1} not found")

        med_2 = self.medication_repository.get_by_id(data.medication_id_2)
        if not med_2:
            raise NotFoundException(f"Medication with id {data.medication_id_2} not found")

        # Validate not same medication
        if data.medication_id_1 == data.medication_id_2:
            raise BadRequestException("Cannot create interaction for a medication with itself")

        # Check if interaction already exists
        existing = self.drug_interaction_repository.get_by_medication_ids(
            data.medication_id_1, data.medication_id_2
        )
        if existing:
            raise ConflictException("Interaction between these medications already exists")

        interaction = DrugInteraction(
            medication_id_1=data.medication_id_1,
            medication_id_2=data.medication_id_2,
            severity=data.severity,
            interaction_description=data.interaction_description
        )
        return self.drug_interaction_repository.create(interaction)

    def update_interaction(self, interaction_id: uuid.UUID, data: DrugInteractionUpdate) -> DrugInteraction:
        interaction = self.drug_interaction_repository.get_by_id(interaction_id)
        if not interaction:
            raise NotFoundException("Drug interaction not found")

        # Update only provided fields
        if data.medication_id_1 is not None:
            # Verify medication exists
            med = self.medication_repository.get_by_id(data.medication_id_1)
            if not med:
                raise NotFoundException(f"Medication with id {data.medication_id_1} not found")
            interaction.medication_id_1 = data.medication_id_1

        if data.medication_id_2 is not None:
            # Verify medication exists
            med = self.medication_repository.get_by_id(data.medication_id_2)
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

        return self.drug_interaction_repository.update(interaction)

    def delete_interaction(self, interaction_id: uuid.UUID) -> None:
        interaction = self.drug_interaction_repository.get_by_id(interaction_id)
        if not interaction:
            raise NotFoundException("Drug interaction not found")
        self.drug_interaction_repository.delete(interaction)
