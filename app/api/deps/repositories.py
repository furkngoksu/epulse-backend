from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.deps.db import get_db
from app.repositories import (
    AppointmentRepository,
    ClinicRepository,
    DoctorPatientRelationshipRepository,
    DoctorProfileRepository,
    DrugInteractionRepository,
    HospitalRepository,
    MedicationAliasRepository,
    MedicationRepository,
    PatientMedicationRepository,
    PrescriptionItemRepository,
    PrescriptionRepository,
    ScheduleRepository,
    ScheduleTimeRepository,
    UserRepository,
)


# User Repository
def get_user_repository(
    db: Session = Depends(get_db),
) -> UserRepository:
    return UserRepository(db)


# Prescription Repositories
def get_prescription_repository(
    db: Session = Depends(get_db),
) -> PrescriptionRepository:
    return PrescriptionRepository(db)


def get_prescription_item_repository(
    db: Session = Depends(get_db),
) -> PrescriptionItemRepository:
    return PrescriptionItemRepository(db)


# Medication Repositories
def get_medication_repository(
    db: Session = Depends(get_db),
) -> MedicationRepository:
    return MedicationRepository(db)


def get_patient_medication_repository(
    db: Session = Depends(get_db),
) -> PatientMedicationRepository:
    return PatientMedicationRepository(db)


def get_medication_alias_repository(
    db: Session = Depends(get_db),
) -> MedicationAliasRepository:
    return MedicationAliasRepository(db)


# Doctor Repositories
def get_doctor_profile_repository(
    db: Session = Depends(get_db),
) -> DoctorProfileRepository:
    return DoctorProfileRepository(db)


def get_doctor_patient_relationship_repository(
    db: Session = Depends(get_db),
) -> DoctorPatientRelationshipRepository:
    return DoctorPatientRelationshipRepository(db)


# Appointment Repository
def get_appointment_repository(
    db: Session = Depends(get_db),
) -> AppointmentRepository:
    return AppointmentRepository(db)


# Hospital Repository
def get_hospital_repository(
    db: Session = Depends(get_db),
) -> HospitalRepository:
    return HospitalRepository(db)


# Clinic Repository
def get_clinic_repository(
    db: Session = Depends(get_db),
) -> ClinicRepository:
    return ClinicRepository(db)


# Drug Interaction Repository
def get_drug_interaction_repository(
    db: Session = Depends(get_db),
) -> DrugInteractionRepository:
    return DrugInteractionRepository(db)


# Schedule Repositories
def get_schedule_repository(
    db: Session = Depends(get_db),
) -> ScheduleRepository:
    return ScheduleRepository(db)


def get_schedule_time_repository(
    db: Session = Depends(get_db),
) -> ScheduleTimeRepository:
    return ScheduleTimeRepository(db)
