import uuid
from itertools import combinations

from app.exceptions.exceptions import NotFoundException, BadRequestException
from app.models import PrescriptionModel, PrescriptionItemModel
from app.repositories import (
    PrescriptionRepository,
    PrescriptionItemRepository,
    DrugInteractionRepository,
    MedicationRepository,
)
from app.models.prescription import Status

from app.schemas.prescription import PrescriptionCreate, PrescriptionUpdate, Prescription
from app.schemas.prescription_item import (
    PrescriptionItem,
    PrescriptionItemCreate,
    PrescriptionItemUpdate,
)
from app.schemas.drug_interaction import DrugInteractionResponse


class PrescriptionService:
    def __init__(
        self,
        prescription_repository: PrescriptionRepository,
        prescription_item_repository: PrescriptionItemRepository,
        drug_interaction_repository: DrugInteractionRepository,
        medication_repository: MedicationRepository,
    ):
        self.prescription_repo = prescription_repository
        self.item_repo = prescription_item_repository
        self.interaction_repo = drug_interaction_repository
        self.med_repo = medication_repository

    # -------------------------
    # Prescriptions
    # -------------------------

    def _ensure_medication_exists(self, medication_id: uuid.UUID) -> None:
        med = self.med_repo.get_by_id(medication_id)
        if not med:
            raise NotFoundException("Medication not found")

    def get_prescription_by_id(self, prescription_id: uuid.UUID) -> Prescription:
        rx = self.prescription_repo.get_by_id(prescription_id=prescription_id)
        if not rx:
            raise NotFoundException("Prescription not found.")
        return Prescription.model_validate(rx)

    def get_prescriptions_by_doctor(self, doctor_id: uuid.UUID, skip: int = 0, limit: int = 50) -> list[Prescription]:
        rows = self.prescription_repo.get_by_doctor_id(doctor_id=doctor_id, skip=skip, limit=limit)
        return [Prescription.model_validate(r) for r in rows]

    def get_prescriptions_by_patient(self, patient_id: uuid.UUID, skip: int = 0, limit: int = 50) -> list[Prescription]:
        rows = self.prescription_repo.get_by_patient_id(patient_id=patient_id, skip=skip, limit=limit)
        return [Prescription.model_validate(r) for r in rows]

    def get_active_prescriptions(self, patient_id: uuid.UUID, skip: int = 0, limit: int = 50) -> list[Prescription]:
        # active alanı yok -> status ile filtrele
        rows = self.prescription_repo.get_by_patient_and_status(
            patient_id=patient_id,
            status=Status.active,
            skip=skip,
            limit=limit,
        )
        return [Prescription.model_validate(r) for r in rows]

    def create_prescription(self, doctor_id: uuid.UUID, data: PrescriptionCreate) -> Prescription:
        # schema patient_id: str -> uuid’a çevir
        try:
            patient_id = uuid.UUID(str(data.patient_id))
        except ValueError:
            raise BadRequestException("Invalid patient_id")

        rx = PrescriptionModel(
            doctor_id=doctor_id,
            patient_id=patient_id,
            notes=data.notes,
            status=Status.inactive
        )
        created = self.prescription_repo.create(prescription=rx)
        return Prescription.model_validate(created)

    def update_prescription(self, prescription_id: uuid.UUID, data: PrescriptionUpdate) -> Prescription:
        rx = self.prescription_repo.get_by_id(prescription_id=prescription_id)
        if not rx:
            raise NotFoundException("Prescription not found.")

        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(rx, k, v)

        updated = self.prescription_repo.update(prescription=rx)
        return Prescription.model_validate(updated)

    def delete_prescription(self, prescription_id: uuid.UUID) -> None:
        rx = self.prescription_repo.get_by_id(prescription_id=prescription_id)
        if not rx:
            raise NotFoundException("Prescription not found.")
        self.prescription_repo.delete(rx)

    def validate_prescription(self, prescription_id: uuid.UUID) -> bool:
        rx = self.prescription_repo.get_by_id(prescription_id=prescription_id)
        if not rx:
            raise NotFoundException("Prescription not found.")
        return bool(rx.items) and all(i.medication_id for i in rx.items)

    # -------------------------
    # Prescription Items
    # -------------------------

    def get_prescription_item_by_id(self, item_id: uuid.UUID) -> PrescriptionItem:
        item = self.item_repo.get_by_id(prescription_item_id=item_id)
        if not item:
            raise NotFoundException("Prescription item not found.")
        return PrescriptionItem.model_validate(item)


    def update_prescription_item(self, item_id: uuid.UUID, data: PrescriptionItemUpdate) -> PrescriptionItem:
        item = self.item_repo.get_by_id(prescription_item_id=item_id)
        if not item:
            raise NotFoundException("Prescription item not found.")

        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(item, k, v)

        updated = self.item_repo.update(prescription_item=item)
        return PrescriptionItem.model_validate(updated)

    def delete_prescription_item(self, item_id: uuid.UUID) -> None:
        item = self.item_repo.get_by_id(prescription_item_id=item_id)
        if not item:
            raise NotFoundException("Prescription item not found.")
        self.item_repo.delete(prescription_item=item)

    def check_prescription_interactions(self, prescription_id: uuid.UUID) -> list[DrugInteractionResponse]:
        rx = self.prescription_repo.get_by_id(prescription_id=prescription_id)
        if not rx:
            raise NotFoundException("Prescription not found.")

        med_ids = [i.medication_id for i in rx.items if i.medication_id]
        # uniq
        med_ids = list(dict.fromkeys(med_ids))

        if len(med_ids) < 2:
            return []

        interactions = []
        for a, b in combinations(med_ids, 2):
            found = self.interaction_repo.get_by_medication_ids(a, b)
            if found:
                interactions.append(found)

        return [DrugInteractionResponse.model_validate(x) for x in interactions]
    
    def get_all_prescription_items(self, prescription_id: uuid.UUID) -> list[PrescriptionItem]:
        rx = self.prescription_repo.get_by_id(prescription_id=prescription_id)
        if not rx:
            raise NotFoundException("Prescription not found.")

        # istersen repo ile:
        items = self.item_repo.get_by_prescription_id(prescription_id)
        return [PrescriptionItem.model_validate(i) for i in items]

    def add_prescription_item(self, data: PrescriptionItemCreate) -> PrescriptionItem:
        rx = self.prescription_repo.get_by_id(prescription_id=data.prescription_id)
        if not rx:
            raise NotFoundException("Prescription not found.")

        self._ensure_medication_exists(data.medication_id)

        item = PrescriptionItemModel(
            prescription_id=data.prescription_id,
            medication_id=data.medication_id,
            dosage=data.dosage,
            duration=data.duration,
        )
        created = self.item_repo.create(item)
        return PrescriptionItem.model_validate(created)


    def add_prescription_items(self, items: list[PrescriptionItemCreate]) -> list[PrescriptionItem]:
        if not items:
            raise BadRequestException("items cannot be empty")

        # hepsi aynı prescription_id mi kontrol (istersen)
        pid = items[0].prescription_id
        if any(i.prescription_id != pid for i in items):
            raise BadRequestException("All items must have same prescription_id")

        rx = self.prescription_repo.get_by_id(prescription_id=pid)
        if not rx:
            raise NotFoundException("Prescription not found.")
        
        med_ids = list({i.medication_id for i in items})
        for mid in med_ids:
            self._ensure_medication_exists(mid)

        models = [
            PrescriptionItemModel(
                prescription_id=i.prescription_id,
                medication_id=i.medication_id,
                dosage=i.dosage,
                duration=i.duration,
            )
            for i in items
        ]

        created = self.item_repo.create_many(models)
        return [PrescriptionItem.model_validate(x) for x in created]
    
    def list_all_prescriptions(self, skip: int = 0, limit: int = 50) -> list[Prescription]:
        rows = self.prescription_repo.get_all(skip=skip, limit=limit)
        return [Prescription.model_validate(r) for r in rows]
