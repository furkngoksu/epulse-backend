from sqlalchemy.orm import Session

from app.models.medication import Medication
from app.repositories.medication import MedicationRepository
from app.schemas.medication import MedicationCreate, MedicationUpdate
from app.exceptions.exceptions import NotFoundException


class MedicationService:

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Medication]:
        return MedicationRepository.get_all(db, skip=skip, limit=limit)

    @staticmethod
    def get_by_id(db: Session, medication_id: int) -> Medication:
        medication = MedicationRepository.get_by_id(db, medication_id)
        if not medication:
            raise NotFoundException("Medication not found")
        return medication

    @staticmethod
    def search_by_name(db: Session, name: str, skip: int = 0, limit: int = 100) -> list[Medication]:
        return MedicationRepository.search_by_name(db, name, skip=skip, limit=limit)

    @staticmethod
    def create(db: Session, data: MedicationCreate) -> Medication:
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
    def update(db: Session, medication_id: int, data: MedicationUpdate) -> Medication:
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
    def delete(db: Session, medication_id: int) -> None:
        medication = MedicationRepository.get_by_id(db, medication_id)
        if not medication:
            raise NotFoundException("Medication not found")
        MedicationRepository.delete(db, medication)
