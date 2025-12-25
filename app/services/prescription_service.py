import uuid
import logging
from itertools import combinations
from typing import Optional

from app.exceptions.exceptions import (
    NotFoundException,
    BadRequestException,
    ForbiddenException,
)
from app.models import PrescriptionModel, PrescriptionItemModel
from app.repositories import (
    PrescriptionRepository,
    PrescriptionItemRepository,
    DrugInteractionRepository,
    MedicationRepository,
)
from app.models.prescription import Status
from app.schemas.prescription import (
    PrescriptionCreate,
    PrescriptionUpdate,
    Prescription,
)
from app.schemas.prescription_item import (
    PrescriptionItem,
    PrescriptionItemCreate,
    PrescriptionItemUpdate,
)
from app.schemas.drug_interaction import DrugInteractionResponse
from app.schemas.user import User

logger = logging.getLogger(__name__)


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
    # Basic helpers
    # -------------------------

    def _ensure_medication_exists(self, medication_id: uuid.UUID) -> None:
        med = self.med_repo.get_by_id(medication_id)
        if not med:
            raise NotFoundException("Medication not found")

    def _get_rx_model(self, prescription_id: uuid.UUID) -> PrescriptionModel:
        rx = self.prescription_repo.get_by_id(prescription_id=prescription_id)
        if not rx:
            raise NotFoundException("Prescription not found.")
        return rx

    def admin_list_prescriptions(
        self,
        skip: int = 0,
        limit: int = 50,
        status: Optional[Status] = None,
    ) -> list[Prescription]:
        rows = self.prescription_repo.get_all(skip=skip, limit=limit, status=status)
        return [Prescription.model_validate(r) for r in rows]

    def doctor_list_prescriptions(
        self,
        doctor_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
        status: Optional[Status] = None,
    ) -> list[Prescription]:
        rows = self.prescription_repo.get_by_doctor_id(
            doctor_id=doctor_id,
            skip=skip,
            limit=limit,
            status=status,
        )
        return [Prescription.model_validate(r) for r in rows]

    def patient_list_prescriptions(
        self,
        patient_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
        status: Optional[Status] = None,
    ) -> list[Prescription]:
        rows = self.prescription_repo.get_by_patient_id(
            patient_id=patient_id,
            skip=skip,
            limit=limit,
            status=status,
        )
        return [Prescription.model_validate(r) for r in rows]

    # -------------------------
    # Prescriptions
    # -------------------------

    def create_prescription(
        self, doctor_id: uuid.UUID, data: PrescriptionCreate
    ) -> Prescription:
        rx = PrescriptionModel(
            doctor_id=doctor_id,
            patient_id=data.patient_id,
            notes=data.notes,
            status=Status.inactive,
        )
        created = self.prescription_repo.create(prescription=rx)
        logger.info(
            "prescription_created",
            extra={
                "prescription_id": str(created.id),
                "patient_id": str(data.patient_id),
            },
        )
        return Prescription.model_validate(created)

    def get_prescription_by_id(
        self, prescription_id: uuid.UUID, current_user: User
    ) -> Prescription:
        rx = self._get_rx_model(prescription_id)

        if rx.doctor_id != current_user.id and rx.patient_id != current_user.id:
            raise ForbiddenException("You do not have access to this prescription")

        return Prescription.model_validate(rx)

    def update_prescription(
        self,
        prescription_id: uuid.UUID,
        data: PrescriptionUpdate,
        current_user: User,
    ) -> Prescription:
        rx = self._get_rx_model(prescription_id)

        if rx.doctor_id != current_user.id:
            raise ForbiddenException(
                "You do not have permission to update this prescription"
            )

        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(rx, k, v)

        updated = self.prescription_repo.update(prescription=rx)
        return Prescription.model_validate(updated)

    def delete_prescription(
        self, prescription_id: uuid.UUID, current_user: User
    ) -> None:
        rx = self._get_rx_model(prescription_id)

        if rx.doctor_id != current_user.id:
            raise ForbiddenException(
                "You do not have permission to delete this prescription"
            )

        self.prescription_repo.delete(rx)

    # -------------------------
    # Items
    # -------------------------

    def get_all_prescription_items(
        self, prescription_id: uuid.UUID, current_user: User
    ) -> list[PrescriptionItem]:
        rx = self._get_rx_model(prescription_id)

        if rx.doctor_id != current_user.id and rx.patient_id != current_user.id:
            raise ForbiddenException("You do not have access to this prescription")

        items = self.item_repo.get_by_prescription_id(prescription_id)
        return [PrescriptionItem.model_validate(i) for i in items]

    def add_prescription_item(
        self,
        prescription_id: uuid.UUID,
        data: PrescriptionItemCreate,
        current_user: User,
    ) -> PrescriptionItem:
        rx = self._get_rx_model(prescription_id)

        if rx.doctor_id != current_user.id:
            raise ForbiddenException(
                "You do not have permission to modify items for this prescription"
            )

        self._ensure_medication_exists(data.medication_id)

        item = PrescriptionItemModel(
            prescription_id=prescription_id,
            medication_id=data.medication_id,
            dosage=data.dosage,
            duration=data.duration,
        )
        created = self.item_repo.create(item)
        logger.info(
            "prescription_item_added",
            extra={
                "prescription_id": str(prescription_id),
                "medication_id": str(data.medication_id),
            },
        )
        return PrescriptionItem.model_validate(created)

    def add_prescription_items(
        self,
        prescription_id: uuid.UUID,
        items: list[PrescriptionItemCreate],
        current_user: User,
    ) -> list[PrescriptionItem]:
        if not items:
            raise BadRequestException("items cannot be empty")

        rx = self._get_rx_model(prescription_id)

        # bulk add doctor-only endpoint
        if rx.doctor_id != current_user.id:
            raise ForbiddenException(
                "You do not have permission to modify items for this prescription"
            )

        med_ids = list({i.medication_id for i in items})
        for mid in med_ids:
            self._ensure_medication_exists(mid)

        models = [
            PrescriptionItemModel(
                prescription_id=prescription_id,
                medication_id=i.medication_id,
                dosage=i.dosage,
                duration=i.duration,
            )
            for i in items
        ]
        created = self.item_repo.create_many(models)
        return [PrescriptionItem.model_validate(x) for x in created]

    def update_prescription_item(
        self,
        item_id: uuid.UUID,
        data: PrescriptionItemUpdate,
        current_user: User,
    ) -> PrescriptionItem:
        item = self.item_repo.get_by_id(prescription_item_id=item_id)
        if not item:
            raise NotFoundException("Prescription item not found.")

        rx = self._get_rx_model(item.prescription_id)

        if rx.doctor_id != current_user.id:
            raise ForbiddenException("You do not have permission to update this item")

        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(item, k, v)

        updated = self.item_repo.update(prescription_item=item)
        return PrescriptionItem.model_validate(updated)

    def delete_prescription_item(self, item_id: uuid.UUID, current_user: User) -> None:
        item = self.item_repo.get_by_id(prescription_item_id=item_id)
        if not item:
            raise NotFoundException("Prescription item not found.")

        rx = self._get_rx_model(item.prescription_id)

        if rx.doctor_id != current_user.id:
            raise ForbiddenException("You do not have permission to delete this item")

        self.item_repo.delete(prescription_item=item)

    # -------------------------
    # Interactions
    # -------------------------

    def check_prescription_interactions(
        self, prescription_id: uuid.UUID, current_user: User
    ) -> list[DrugInteractionResponse]:
        rx = self._get_rx_model(prescription_id)

        if rx.doctor_id != current_user.id and rx.patient_id != current_user.id:
            raise ForbiddenException("You do not have access to this prescription")

        med_ids = [i.medication_id for i in rx.items if i.medication_id]
        med_ids = list(dict.fromkeys(med_ids))
        if len(med_ids) < 2:
            return []

        interactions = []
        for a, b in combinations(med_ids, 2):
            found = self.interaction_repo.get_by_medication_ids(a, b)
            if found:
                interactions.append(found)

        return [DrugInteractionResponse.model_validate(x) for x in interactions]
