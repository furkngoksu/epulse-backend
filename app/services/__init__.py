from .auth_service import AuthService
from .prescription_service import PrescriptionService
from .appointment_service import AppointmentService
from .doctor_patient_relationship_service import DoctorPatientRelationshipService
from .doctor_profile_service import DoctorProfileService
from .drug_interaction_service import DrugInteractionService
from .hospital_service import HospitalService
from .medication_service import MedicationService

# Doctor patient relationship servisleri domain bazlıya çeviririz sonra burayı düzenleriz kod sadeleşsin diye yapıyom


__all__ = [
    "AuthService",
    "PrescriptionService",
    "AppointmentService",
    "DoctorPatientRelationshipService",
    "DoctorProfileService",
    "DrugInteractionService",
    "HospitalService",
    "MedicationService"
]