from fastapi import Depends

from app.api.deps.auth import get_current_user
from app.api.deps.repositories import (
    get_appointment_repository,
    get_doctor_patient_relationship_repository,
    get_doctor_profile_repository,
    get_drug_interaction_repository,
    get_hospital_repository,
    get_medication_repository,
    get_prescription_item_repository,
    get_prescription_repository,
    get_user_repository,
)
from app.repositories.appointment import AppointmentRepository
from app.repositories.doctor_patient_relationship import DoctorPatientRelationshipRepository
from app.repositories.doctor_profile_repository import DoctorProfileRepository
from app.repositories.drug_interaction import DrugInteractionRepository
from app.repositories.hospital import HospitalRepository
from app.repositories.medication_repository import MedicationRepository
from app.repositories.prescription_item_repository import PrescriptionItemRepository
from app.repositories.prescription_repository import PrescriptionRepository
from app.repositories.user import UserRepository
from app.schemas.user import User
from app.services.appointment_service import AppointmentService
from app.services.catalog_service import CatalogService
from app.services.doctor_service import DoctorService
from app.services.prescription_service import PrescriptionService


# Prescription Service
def get_prescription_service(
    prescription_repository: PrescriptionRepository = Depends(get_prescription_repository),
    prescription_item_repository: PrescriptionItemRepository = Depends(get_prescription_item_repository),
    current_user: User = Depends(get_current_user),
) -> PrescriptionService:
    return PrescriptionService(
        prescription_repository=prescription_repository,
        prescription_item_repository=prescription_item_repository,
        current_user=current_user,
    )


# Appointment Service
def get_appointment_service(
    appointment_repository: AppointmentRepository = Depends(get_appointment_repository),
    user_repository: UserRepository = Depends(get_user_repository),
    doctor_patient_relationship_repository: DoctorPatientRelationshipRepository = Depends(get_doctor_patient_relationship_repository),
) -> AppointmentService:
    return AppointmentService(
        appointment_repository=appointment_repository,
        user_repository=user_repository,
        doctor_patient_relationship_repository=doctor_patient_relationship_repository,
    )


# Doctor Service
def get_doctor_service(
    hospital_repository: HospitalRepository = Depends(get_hospital_repository),
    doctor_profile_repository: DoctorProfileRepository = Depends(get_doctor_profile_repository),
    doctor_patient_relationship_repository: DoctorPatientRelationshipRepository = Depends(get_doctor_patient_relationship_repository),
    user_repository: UserRepository = Depends(get_user_repository),
) -> DoctorService:
    return DoctorService(
        hospital_repository=hospital_repository,
        doctor_profile_repository=doctor_profile_repository,
        doctor_patient_relationship_repository=doctor_patient_relationship_repository,
        user_repository=user_repository,
    )


# Catalog Service
def get_catalog_service(
    medication_repository: MedicationRepository = Depends(get_medication_repository),
    drug_interaction_repository: DrugInteractionRepository = Depends(get_drug_interaction_repository),
) -> CatalogService:
    return CatalogService(
        medication_repository=medication_repository,
        drug_interaction_repository=drug_interaction_repository,
    )
