# Database
from app.api.deps.db import get_db

# Repositories
from app.api.deps.repositories import (
    get_user_repository,
    get_prescription_repository,
    get_prescription_item_repository,
    get_medication_repository,
    get_patient_medication_repository,
    get_doctor_profile_repository,
    get_doctor_patient_relationship_repository,
    get_appointment_repository,
    get_hospital_repository,
    get_drug_interaction_repository,
    get_dose_log_repository,
    get_schedule_repository,
    get_schedule_time_repository,
)

# Services
from app.api.deps.services import (
    get_prescription_service,
    get_appointment_service,
    get_doctor_service,
    get_catalog_service,
)

# Auth
from app.api.deps.auth import (
    get_current_user,
    get_current_admin,
    get_current_doctor,
    get_current_doctor_or_admin,
    get_auth_service,
)

__all__ = [
    # Database
    "get_db",
    # Repositories
    "get_user_repository",
    "get_prescription_repository",
    "get_prescription_item_repository",
    "get_medication_repository",
    "get_patient_medication_repository",
    "get_doctor_profile_repository",
    "get_doctor_patient_relationship_repository",
    "get_appointment_repository",
    "get_hospital_repository",
    "get_drug_interaction_repository",
    "get_dose_log_repository",
    "get_schedule_repository",
    "get_schedule_time_repository",
    # Services
    "get_auth_service",
    "get_prescription_service",
    "get_appointment_service",
    "get_doctor_service",
    "get_catalog_service",
    # Auth
    "get_current_user",
    "get_current_admin",
    "get_current_doctor",
    "get_current_doctor_or_admin",
]
