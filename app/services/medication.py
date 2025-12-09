from app.models import MedicationModel
from app.repositories.medication import MedicationRepository
from app.schemas.medication import MedicationCreate, MedicationUpdate
from app.exceptions.exceptions import NotFoundException
from app.schemas.medication import Medication


class MedicationService:

    def __init__(self, medication_repository: MedicationRepository):
        self.medication_repository = medication_repository

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Medication]:
        medications = self.medication_repository.get_all(skip=skip, limit=limit)
        return [Medication.model_validate(m) for m in medications]

    def get_by_id(self, medication_id: int) -> Medication:
        medication = self.medication_repository.get_by_id(medication_id)
        if not medication:
            raise NotFoundException("Medication not found")
        return Medication.model_validate(medication)

    def search_by_name(self, name: str, skip: int = 0, limit: int = 100) -> list[Medication]:
        medications = self.medication_repository.search_by_name(name, skip=skip, limit=limit)
        return [Medication.model_validate(m) for m in medications]

    def create(self, data: MedicationCreate) -> Medication:
        new_medication = MedicationModel(**data.model_dump())
        medication = self.medication_repository.create(new_medication)
        return Medication.model_validate(medication)

    def update(self, medication_id: int, data: MedicationUpdate) -> Medication:
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

        updated_medication = self.medication_repository.update(medication)
        return Medication.model_validate(updated_medication)

    def delete(self, medication_id: int) -> None:
        medication = self.medication_repository.get_by_id(medication_id)
        if not medication:
            raise NotFoundException("Medication not found")
        self.medication_repository.delete(medication)
