from fastapi import Depends

from app.api.deps.repositories import (
    get_appointment_repository,
    get_doctor_patient_relationship_repository,
    get_doctor_profile_repository,
    get_drug_interaction_repository,
    get_hospital_repository,
    get_medication_repository,
    get_patient_medication_repository,
    get_prescription_item_repository,
    get_prescription_repository,
    get_schedule_repository,
    get_schedule_time_repository,
    get_user_repository,
)

from app.services import DoctorService, MedicationService, CatalogService, PrescriptionService, AppointmentService, UserService
from app.repositories import (
    PrescriptionRepository, 
    PrescriptionItemRepository, 
    DrugInteractionRepository, 
    MedicationRepository, 
    PatientMedicationRepository, 
    ScheduleRepository, 
    ScheduleTimeRepository, 
    DoctorProfileRepository, 
    HospitalRepository, 
    UserRepository,
    AppointmentRepository,
    DoctorPatientRelationshipRepository,
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

# Medication Service
def get_medication_service(
    medication_repo: MedicationRepository = Depends(get_medication_repository),
    patient_medication_repo: PatientMedicationRepository = Depends(get_patient_medication_repository),
    schedule_repo: ScheduleRepository = Depends(get_schedule_repository),
    schedule_time_repo: ScheduleTimeRepository = Depends(get_schedule_time_repository),
) -> MedicationService:
    return MedicationService(
        medication_repo=medication_repo,
        patient_medication_repo=patient_medication_repo,
        schedule_repo=schedule_repo,
        schedule_time_repo=schedule_time_repo,
    )

def get_prescription_service(
    prescription_repository: PrescriptionRepository = Depends(get_prescription_repository),
    prescription_item_repository: PrescriptionItemRepository = Depends(get_prescription_item_repository),
    drug_interaction_repository: DrugInteractionRepository = Depends(get_drug_interaction_repository),
    medication_repository: MedicationRepository = Depends(get_medication_repository),
) -> PrescriptionService:
    return PrescriptionService(
        prescription_repository=prescription_repository,
        prescription_item_repository=prescription_item_repository,
        drug_interaction_repository=drug_interaction_repository,
        medication_repository=medication_repository,
    )

# User Service
def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(user_repo=user_repository)