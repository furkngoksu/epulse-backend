from app.models.prescription import Status
from app.models.prescription_item import PrescriptionItemModel
from app.models.user import RoleEnum
from app.repositories import PrescriptionRepository, PrescriptionItemRepository
from app.schemas import User
from app.schemas.prescription_item import PrescriptionItem, PrescriptionItemCreate, PrescriptionItemUpdate
from app.models import PrescriptionModel
import uuid  
from app.schemas.prescription import PrescriptionCreate, PrescriptionUpdate, Prescription
from app.exceptions import ForbiddenException, NotFoundException

class PrescriptionService:
    def __init__(self, 
        prescription_repository: PrescriptionRepository,
        prescription_item_repository: PrescriptionItemRepository,
        current_user: User
    ):
        self.current_user = current_user
        self.prescription_repository = prescription_repository
        self.prescription_item_repository = prescription_item_repository


    def get_all_prescriptions(self) -> list[Prescription]:
        prescriptions = self.prescription_repository.get_all()
        return [Prescription.model_validate(p) for p in prescriptions]

    def get_prescription_by_id(self, prescription_id: uuid.UUID) -> Prescription | None:
        prescription = self.prescription_repository.get_by_id(prescription_id=prescription_id)
        return Prescription.model_validate(prescription) if prescription else None

    def get_prescriptions_by_doctor(self, doctor_id: uuid.UUID, skip: int = 0, limit: int = 50) -> list[Prescription]:
        prescriptions = self.prescription_repository.get_by_doctor_id(doctor_id=doctor_id, skip=skip, limit=limit)
        return [Prescription.model_validate(p) for p in prescriptions]

    def get_prescriptions_by_patient(self, patient_id: uuid.UUID, skip: int = 0, limit: int = 50) -> list[Prescription]:
        prescriptions = self.prescription_repository.get_by_patient_id(patient_id=patient_id, skip=skip, limit=limit)
        return [Prescription.model_validate(p) for p in prescriptions]

    def create_prescription(self, data: PrescriptionCreate) -> Prescription:

        new_prescription = PrescriptionModel(
            doctor_id=self.current_user.id,
            patient_id=data.patient_id,
            notes=data.notes,
            status=Status.inactive
        )

        created = self.prescription_repository.create(prescription=new_prescription)
        return Prescription.model_validate(created)

    def update_prescription(self, prescription_id: uuid.UUID, data: PrescriptionUpdate) -> Prescription:

        prescription = self.prescription_repository.get_by_id(prescription_id=prescription_id)
        if not prescription:
            raise NotFoundException("Prescription not found.")

        if data.notes is not None:
            prescription.notes = data.notes
        if data.status is not None:
            prescription.status = data.status

        updated = self.prescription_repository.update(prescription=prescription)
        return Prescription.model_validate(updated)

    def delete_prescription(self, prescription_id: uuid.UUID) -> None:

        prescription = self.prescription_repository.get_by_id(prescription_id=prescription_id)
        if not prescription:
            raise NotFoundException("Prescription not found.")
        
        if self.current_user.role == RoleEnum.doctor and prescription.doctor_id != self.current_user.id:
            raise ForbiddenException("Doctors can only modify their own prescriptions.")

        self.prescription_repository.delete(prescription)

    # Prescription Item Methods

    def get_prescription_item_by_id(self, item_id: uuid.UUID) -> PrescriptionItem | None:
        item = self.prescription_item_repository.get_by_id(prescription_item_id=item_id)
        return PrescriptionItem.model_validate(item) if item else None

    def get_all_prescription_items(self, prescription_id: uuid.UUID) -> list[PrescriptionItem]:

        prescription = self.prescription_repository.get_by_id(prescription_id=prescription_id)
        if not prescription:
            raise NotFoundException("Prescription not found.")

        items = prescription.items
        return [PrescriptionItem.model_validate(i) for i in items]

    def add_prescription_item(self, prescription_id: uuid.UUID, data: PrescriptionItemCreate) -> PrescriptionItem:

        prescription = self.prescription_repository.get_by_id(prescription_id=prescription_id)
        if not prescription:
            raise NotFoundException("Prescription not found.")

        if self.current_user.role == RoleEnum.doctor and prescription.doctor_id != self.current_user.id:
            raise ForbiddenException("Doctors can only modify their own prescriptions.")

        new_item = PrescriptionItemModel(
            prescription_id=prescription_id,
            medication_id=data.medication_id,
            dosage=data.dosage,
            duration=data.duration
        )

        created = self.prescription_item_repository.create(prescription_item=new_item)
        return PrescriptionItem.model_validate(created)

    def update_prescription_item(self, item_id: uuid.UUID, data: PrescriptionItemUpdate) -> PrescriptionItem:

        item = self.prescription_item_repository.get_by_id(prescription_item_id=item_id)
        if not item:
            raise NotFoundException("Prescription item not found.")

        prescription = self.prescription_repository.get_by_id(prescription_id=item.prescription_id)
        if not prescription:
            raise NotFoundException("Prescription not found.")

        if self.current_user.role == RoleEnum.doctor and prescription.doctor_id != self.current_user.id:
            raise ForbiddenException("Doctors can only modify their own prescriptions.")

        if data.dosage is not None:
            item.dosage = data.dosage
        if data.duration is not None:
            item.duration = data.duration

        updated = self.prescription_item_repository.update(prescription_item=item)
        return PrescriptionItem.model_validate(updated)

    def delete_prescription_item(self, item_id: uuid.UUID) -> None:

        item = self.prescription_item_repository.get_by_id(prescription_item_id=item_id)
        if not item:
            raise NotFoundException("Prescription item not found.")

        prescription = self.prescription_repository.get_by_id(prescription_id=item.prescription_id)
        if not prescription:
            raise NotFoundException("Prescription not found.")

        if self.current_user.role == RoleEnum.doctor and prescription.doctor_id != self.current_user.id:
            raise ForbiddenException("Doctors can only delete items from their own prescriptions.")

        self.prescription_item_repository.delete(prescription_item=item)

    def validate_prescription(self, prescription_id: uuid.UUID) -> bool:
        prescription = self.prescription_repository.get_by_id(prescription_id=prescription_id)
        if not prescription:
            raise NotFoundException("Prescription not found.")

        items = prescription.items

        if not items:
            return False

        for item in items:
            if item.medication_id is None:
                return False

        return True