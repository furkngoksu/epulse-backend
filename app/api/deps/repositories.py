from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.deps.db import get_db
from app.repositories.appointment import AppointmentRepository
from app.repositories.doctor_patient_relationship import DoctorPatientRelationshipRepository
from app.repositories.doctor_profile_repository import DoctorProfileRepository
from app.repositories.dose_log_repository import DoseLogRepository
from app.repositories.drug_interaction import DrugInteractionRepository
from app.repositories.hospital import HospitalRepository
from app.repositories.medication_repository import MedicationRepository
from app.repositories.patient_medication_repository import PatientMedicationRepository
from app.repositories.prescription_item_repository import PrescriptionItemRepository
from app.repositories.prescription_repository import PrescriptionRepository
from app.repositories.schedule_repository import ScheduleRepository, ScheduleTimeRepository
from app.repositories.user import UserRepository


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


# Drug Interaction Repository
def get_drug_interaction_repository(
    db: Session = Depends(get_db),
) -> DrugInteractionRepository:
    return DrugInteractionRepository(db)


# Dose Log Repository
def get_dose_log_repository(
    db: Session = Depends(get_db),
) -> DoseLogRepository:
    return DoseLogRepository(db)


# Schedule Repositories
def get_schedule_repository(
    db: Session = Depends(get_db),
) -> ScheduleRepository:
    return ScheduleRepository(db)


def get_schedule_time_repository(
    db: Session = Depends(get_db),
) -> ScheduleTimeRepository:
    return ScheduleTimeRepository(db)
