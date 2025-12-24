import uuid
import logging
from typing import Optional

from app.exceptions import NotFoundException, BadRequestException, ConflictException
from app.models import DrugInteractionModel, MedicationModel
from app.repositories import DrugInteractionRepository, MedicationRepository

from app.schemas.medication import MedicationCreate, MedicationUpdate, MedicationResponse
from app.schemas.drug_interaction import (
    DrugInteractionCreate,
    DrugInteractionUpdate,
    DrugInteractionResponse,
)

logger = logging.getLogger(__name__)


class CatalogService:
    
    def __init__(
        self,
        medication_repository: MedicationRepository,
        drug_interaction_repository: DrugInteractionRepository,
    ):
        self.med_repo = medication_repository
        self.di_repo = drug_interaction_repository

    # =========================
    # Medications
    # =========================

    def list_medications(
        self,
        skip: int = 0,
        limit: int = 100,
        query: Optional[str] = None,
    ) -> list[MedicationResponse]:
        rows = self.med_repo.get_all(skip=skip, limit=limit, q=query)

        return [MedicationResponse.model_validate(x) for x in rows]

    def get_medication_by_id(self, medication_id: uuid.UUID) -> MedicationResponse:
        row = self.med_repo.get_by_id(medication_id)
        if not row:
            raise NotFoundException("Medication not found")
        return MedicationResponse.model_validate(row)

    def create_medication(self, data: MedicationCreate) -> MedicationResponse:
        model = MedicationModel(**data.model_dump())
        created = self.med_repo.create(model)
        logger.info("Medication created successfully", extra={"medication_id": str(created.id), "name": created.commercial_name})
        return MedicationResponse.model_validate(created)

    def update_medication(self, medication_id: uuid.UUID, data: MedicationUpdate) -> MedicationResponse:
        row = self.med_repo.get_by_id(medication_id)
        if not row:
            raise NotFoundException("Medication not found")

        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(row, k, v)

        updated = self.med_repo.update(row)
        return MedicationResponse.model_validate(updated)

    def delete_medication(self, medication_id: uuid.UUID) -> None:
        row = self.med_repo.get_by_id(medication_id)
        if not row:
            raise NotFoundException("Medication not found")
        self.med_repo.delete(row)

    # =========================
    # Drug Interactions
    # =========================

    def get_all_interactions(self, skip: int = 0, limit: int = 100) -> list[DrugInteractionResponse]:
        rows = self.di_repo.get_all(skip=skip, limit=limit)
        return [DrugInteractionResponse.model_validate(x) for x in rows]

    def get_interaction_by_id(self, interaction_id: uuid.UUID) -> DrugInteractionResponse:
        row = self.di_repo.get_by_id(interaction_id)
        if not row:
            raise NotFoundException("Drug interaction not found")
        return DrugInteractionResponse.model_validate(row)

    def check_interaction(self, med_id_1: uuid.UUID, med_id_2: uuid.UUID) -> Optional[DrugInteractionResponse]:
        
        if med_id_1 == med_id_2:
            raise BadRequestException("Cannot check interaction of a medication with itself")
        
        a, b = sorted([med_id_1, med_id_2], key=lambda x: str(x))

        found = self.di_repo.get_by_medication_ids(a, b)
        return DrugInteractionResponse.model_validate(found) if found else None

    def get_interactions_for_medication(self, medication_id: uuid.UUID) -> list[DrugInteractionResponse]:
        med = self.med_repo.get_by_id(medication_id)
        if not med:
            raise NotFoundException("Medication not found")

        rows = self.di_repo.get_interactions_for_medication(medication_id)
        return [DrugInteractionResponse.model_validate(x) for x in rows]

    def create_interaction(self, data: DrugInteractionCreate) -> DrugInteractionResponse:
        if data.medication_id_1 == data.medication_id_2:
            raise BadRequestException("Cannot create interaction for a medication with itself")

        a, b = sorted([data.medication_id_1, data.medication_id_2], key=lambda x: str(x))

        if not self.med_repo.get_by_id(a):
            raise NotFoundException(f"Medication with id {a} not found")
        if not self.med_repo.get_by_id(b):
            raise NotFoundException(f"Medication with id {b} not found")

        existing = self.di_repo.get_by_medication_ids(a, b)
        if existing:
            raise ConflictException("Interaction between these medications already exists")

        model = DrugInteractionModel(
            medication_id_1=a,
            medication_id_2=b,
            severity=data.severity,
            interaction_description=data.interaction_description,
        )
        created = self.di_repo.create(model)
        return DrugInteractionResponse.model_validate(created)

    def update_interaction(self, interaction_id: uuid.UUID, data: DrugInteractionUpdate) -> DrugInteractionResponse:
        row = self.di_repo.get_by_id(interaction_id)
        if not row:
            raise NotFoundException("Drug interaction not found")

        patch = data.model_dump(exclude_unset=True)

        if "medication_id_1" in patch and patch["medication_id_1"] is not None:
            if not self.med_repo.get_by_id(patch["medication_id_1"]):
                raise NotFoundException(f"Medication with id {patch['medication_id_1']} not found")
            row.medication_id_1 = patch["medication_id_1"]

        if "medication_id_2" in patch and patch["medication_id_2"] is not None:
            if not self.med_repo.get_by_id(patch["medication_id_2"]):
                raise NotFoundException(f"Medication with id {patch['medication_id_2']} not found")
            row.medication_id_2 = patch["medication_id_2"]

        if row.medication_id_1 == row.medication_id_2:
            raise BadRequestException("Cannot create interaction for a medication with itself")
        
        a, b = sorted([row.medication_id_1, row.medication_id_2], key=lambda x: str(x))
        row.medication_id_1 = a
        row.medication_id_2 = b

        # Check for duplicate interaction
        existing = self.di_repo.get_by_medication_ids(row.medication_id_1, row.medication_id_2)
        if existing and existing.id != row.id:
            raise ConflictException("Interaction between these medications already exists")

        # rest fields
        if "severity" in patch and patch["severity"] is not None:
            row.severity = patch["severity"]
        if "interaction_description" in patch:
            row.interaction_description = patch["interaction_description"]

        updated = self.di_repo.update(row)
        return DrugInteractionResponse.model_validate(updated)

    def delete_interaction(self, interaction_id: uuid.UUID) -> None:
        row = self.di_repo.get_by_id(interaction_id)
        if not row:
            raise NotFoundException("Drug interaction not found")
        self.di_repo.delete(row)