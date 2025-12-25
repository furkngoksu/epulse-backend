import uuid
import logging
from typing import TYPE_CHECKING
from app.models.hospital import Hospital
from app.models.clinic import Clinic
from app.models.doctor_profile import DoctorProfile
from app.models.doctor_patient_relationship import DoctorPatientRelationship
from app.models.user import RoleEnum
from app.repositories.hospital_repository import HospitalRepository
from app.repositories.clinic_repository import ClinicRepository
from app.repositories.doctor_profile_repository import DoctorProfileRepository
from app.repositories.doctor_patient_repository import (
    DoctorPatientRelationshipRepository,
)
from app.repositories.user_repository import UserRepository
from app.schemas.hospital import HospitalCreate, HospitalUpdate
from app.schemas.clinic import ClinicCreate, ClinicUpdate
from app.schemas.doctor_profile import (
    DoctorProfileCreate,
    DoctorProfileUpdate,
    DoctorProfileResponse,
)
from app.schemas.doctor_patient_relationship import DoctorPatientRelationshipCreate
from app.exceptions.exceptions import (
    NotFoundException,
    BadRequestException,
    ConflictException,
)

if TYPE_CHECKING:
    from app.services.report_service import ReportService

logger = logging.getLogger(__name__)


class DoctorService:
    """
    Consolidated service for managing hospitals, clinics, doctor profiles, and doctor-patient relationships.
    """

    def __init__(
        self,
        hospital_repository: HospitalRepository,
        clinic_repository: ClinicRepository,
        doctor_profile_repository: DoctorProfileRepository,
        doctor_patient_relationship_repository: DoctorPatientRelationshipRepository,
        user_repository: UserRepository,
        report_service: "ReportService",
    ):
        self.hospital_repository = hospital_repository
        self.clinic_repository = clinic_repository
        self.doctor_profile_repository = doctor_profile_repository
        self.doctor_patient_relationship_repository = (
            doctor_patient_relationship_repository
        )
        self.user_repository = user_repository
        self.report_service = report_service

    @staticmethod
    def _to_doctor_profile_response(profile: DoctorProfile) -> DoctorProfileResponse:
        """Convert DoctorProfile model to DoctorProfileResponse schema."""
        return DoctorProfileResponse(
            id=profile.id,
            first_name=profile.user.first_name,
            last_name=profile.user.last_name,
            specialty=profile.specialty,
            hospital_id=profile.clinic.hospital_id,
            hospital_name=profile.clinic.hospital.name,
            clinic_id=profile.clinic_id,
            clinic_name=profile.clinic.name,
        )

    # ==================== Hospital Methods ====================

    def get_all_hospitals(self, skip: int = 0, limit: int = 100) -> list[Hospital]:
        return self.hospital_repository.get_all(skip=skip, limit=limit)

    def get_hospital_by_id(self, hospital_id: uuid.UUID) -> Hospital:
        hospital = self.hospital_repository.get_by_id(hospital_id)
        if not hospital:
            raise NotFoundException("Hospital not found")
        return hospital

    def create_hospital(self, data: HospitalCreate) -> Hospital:
        hospital = Hospital(
            name=data.name,
            address=data.address,
            city=data.city,
            district=data.district,
            phone=data.phone,
        )
        return self.hospital_repository.create(hospital)

    def update_hospital(self, hospital_id: uuid.UUID, data: HospitalUpdate) -> Hospital:
        hospital = self.hospital_repository.get_by_id(hospital_id)
        if not hospital:
            raise NotFoundException("Hospital not found")

        # Update only provided fields
        if data.name is not None:
            hospital.name = data.name
        if data.address is not None:
            hospital.address = data.address
        if data.city is not None:
            hospital.city = data.city
        if data.district is not None:
            hospital.district = data.district
        if data.phone is not None:
            hospital.phone = data.phone

        return self.hospital_repository.update(hospital)

    def delete_hospital(self, hospital_id: uuid.UUID) -> None:
        hospital = self.hospital_repository.get_by_id(hospital_id)
        if not hospital:
            raise NotFoundException("Hospital not found")
        self.hospital_repository.delete(hospital)

    # ==================== Clinic Methods ====================

    def get_all_clinics(self, skip: int = 0, limit: int = 100) -> list[Clinic]:
        return self.clinic_repository.get_all(skip=skip, limit=limit)

    def get_clinic_by_id(self, clinic_id: uuid.UUID) -> Clinic:
        clinic = self.clinic_repository.get_by_id(clinic_id)
        if not clinic:
            raise NotFoundException("Clinic not found")
        return clinic

    def get_clinics_by_hospital(self, hospital_id: uuid.UUID) -> list[Clinic]:
        # Verify hospital exists
        hospital = self.hospital_repository.get_by_id(hospital_id)
        if not hospital:
            raise NotFoundException("Hospital not found")

        return self.clinic_repository.get_by_hospital_id(hospital_id)

    def create_clinic(self, data: ClinicCreate) -> Clinic:
        # Verify hospital exists
        hospital = self.hospital_repository.get_by_id(data.hospital_id)
        if not hospital:
            raise NotFoundException("Hospital not found")

        clinic = Clinic(name=data.name, hospital_id=data.hospital_id)
        return self.clinic_repository.create(clinic)

    def update_clinic(self, clinic_id: uuid.UUID, data: ClinicUpdate) -> Clinic:
        clinic = self.clinic_repository.get_by_id(clinic_id)
        if not clinic:
            raise NotFoundException("Clinic not found")

        # Update only provided fields
        if data.name is not None:
            clinic.name = data.name
        if data.hospital_id is not None:
            # Verify hospital exists
            hospital = self.hospital_repository.get_by_id(data.hospital_id)
            if not hospital:
                raise NotFoundException("Hospital not found")
            clinic.hospital_id = data.hospital_id

        return self.clinic_repository.update(clinic)

    def delete_clinic(self, clinic_id: uuid.UUID) -> None:
        clinic = self.clinic_repository.get_by_id(clinic_id)
        if not clinic:
            raise NotFoundException("Clinic not found")
        self.clinic_repository.delete(clinic)

    # ==================== Doctor Profile Methods ====================

    def get_all_doctor_profiles(
        self, skip: int = 0, limit: int = 100
    ) -> list[DoctorProfileResponse]:
        profiles = self.doctor_profile_repository.get_all(skip=skip, limit=limit)
        return [self._to_doctor_profile_response(profile) for profile in profiles]

    def get_doctor_profile_by_id(self, profile_id: uuid.UUID) -> DoctorProfileResponse:
        profile = self.doctor_profile_repository.get_by_id(profile_id)
        if not profile:
            raise NotFoundException("Doctor profile not found")
        return self._to_doctor_profile_response(profile)

    def get_doctors_by_clinic(
        self, clinic_id: uuid.UUID
    ) -> list[DoctorProfileResponse]:
        # Verify clinic exists
        clinic = self.clinic_repository.get_by_id(clinic_id)
        if not clinic:
            raise NotFoundException("Clinic not found")

        profiles = self.doctor_profile_repository.get_by_clinic_id(clinic_id)
        return [self._to_doctor_profile_response(profile) for profile in profiles]

    def create_doctor_profile(self, data: DoctorProfileCreate) -> DoctorProfileResponse:
        # Verify user exists
        user = self.user_repository.get_by_id(data.user_id)
        if not user:
            raise NotFoundException("User not found")

        # Update user role to doctor if not already
        if user.role != RoleEnum.doctor:
            user.role = RoleEnum.doctor
            self.user_repository.update(user)

        # Check if profile already exists for this user
        existing_profile = self.doctor_profile_repository.get_by_user_id(data.user_id)
        if existing_profile:
            raise ConflictException("Doctor profile already exists for this user")

        # Verify clinic exists
        clinic = self.clinic_repository.get_by_id(data.clinic_id)
        if not clinic:
            raise NotFoundException("Clinic not found")

        profile = DoctorProfile(
            id=data.user_id, clinic_id=data.clinic_id, specialty=data.specialty
        )
        created_profile = self.doctor_profile_repository.create(profile)

        logger.info(
            "Doctor profile created successfully",
            extra={"user_id": str(data.user_id), "clinic_id": str(data.clinic_id)},
        )

        # Fetch the profile with all relations to return proper response
        profile_with_relations = self.doctor_profile_repository.get_by_id(
            created_profile.id
        )
        return self._to_doctor_profile_response(profile_with_relations)

    def update_doctor_profile(
        self, profile_id: uuid.UUID, data: DoctorProfileUpdate
    ) -> DoctorProfileResponse:
        profile = self.doctor_profile_repository.get_by_id(profile_id)
        if not profile:
            raise NotFoundException("Doctor profile not found")

        # Update only provided fields
        if data.clinic_id is not None:
            # Verify clinic exists
            clinic = self.clinic_repository.get_by_id(data.clinic_id)
            if not clinic:
                raise NotFoundException("Clinic not found")
            profile.clinic_id = data.clinic_id

        if data.specialty is not None:
            profile.specialty = data.specialty

        updated_profile = self.doctor_profile_repository.update(profile)

        # Fetch the profile with all relations to return proper response
        profile_with_relations = self.doctor_profile_repository.get_by_id(
            updated_profile.id
        )
        return self._to_doctor_profile_response(profile_with_relations)

    def delete_doctor_profile(self, profile_id: uuid.UUID) -> None:
        profile = self.doctor_profile_repository.get_by_id(profile_id)
        if not profile:
            raise NotFoundException("Doctor profile not found")
        self.doctor_profile_repository.delete(profile)

    # ==================== Doctor-Patient Relationship Methods ====================

    def get_all_relationships(
        self, skip: int = 0, limit: int = 100
    ) -> list[DoctorPatientRelationship]:
        return self.doctor_patient_relationship_repository.get_all(
            skip=skip, limit=limit
        )

    def get_relationship_by_id(
        self, relationship_id: uuid.UUID
    ) -> DoctorPatientRelationship:
        relationship = self.doctor_patient_relationship_repository.get_by_id(
            relationship_id
        )
        if not relationship:
            raise NotFoundException("Doctor-patient relationship not found")
        return relationship

    def get_doctor_patients(
        self, doctor_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[DoctorPatientRelationship]:
        """Get all patients for a specific doctor."""
        # Verify doctor exists and has doctor role
        doctor = self.user_repository.get_by_id(doctor_id)
        if not doctor:
            raise NotFoundException("Doctor not found")
        if doctor.role != RoleEnum.doctor:
            raise BadRequestException("User is not a doctor")

        return self.doctor_patient_relationship_repository.get_patients_for_doctor(
            doctor_id, skip, limit
        )

    def get_doctor_patient_summaries(
        self, doctor_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[dict]:
        """Get patient summaries with basic info and statistics for a specific doctor."""
        # Verify doctor exists and has doctor role
        doctor = self.user_repository.get_by_id(doctor_id)
        if not doctor:
            raise NotFoundException("Doctor not found")
        if doctor.role != RoleEnum.doctor:
            raise BadRequestException("User is not a doctor")

        # Get basic patient list from repository
        relationships = (
            self.doctor_patient_relationship_repository.get_patients_for_doctor(
                doctor_id, skip, limit
            )
        )

        # Use ReportService to get statistics for each patient
        patient_summaries = []
        for relationship in relationships:
            patient_id = relationship.patient_id

            # Get basic stats from ReportService
            try:
                stats = self.report_service.get_basic_stats(patient_id=patient_id)
                patient_summaries.append(
                    {
                        "patient_id": stats.patient_id,
                        "first_name": stats.first_name,
                        "last_name": stats.last_name,
                        "age": stats.age,
                        "active_prescriptions": stats.active_medications_count,
                        "adherence_rate": stats.overall_adherence_rate,
                        "pending_doses_today": stats.pending_doses_today,
                    }
                )
            except Exception:
                # If stats fail for a patient, skip them
                continue

        return patient_summaries

    def get_patient_doctors(
        self, patient_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[DoctorPatientRelationship]:
        """Get all doctors for a specific patient."""
        # Verify patient exists and has patient role
        patient = self.user_repository.get_by_id(patient_id)
        if not patient:
            raise NotFoundException("Patient not found")
        if patient.role != RoleEnum.patient:
            raise BadRequestException("User is not a patient")

        return self.doctor_patient_relationship_repository.get_doctors_for_patient(
            patient_id, skip, limit
        )

    def create_doctor_patient_relationship(
        self, data: DoctorPatientRelationshipCreate
    ) -> DoctorPatientRelationship:
        # Validate doctor exists and has doctor role
        doctor = self.user_repository.get_by_id(data.doctor_id)
        if not doctor:
            raise NotFoundException(f"Doctor with id {data.doctor_id} not found")
        if doctor.role != RoleEnum.doctor:
            raise BadRequestException(f"User with id {data.doctor_id} is not a doctor")

        # Validate patient exists and has patient role
        patient = self.user_repository.get_by_id(data.patient_id)
        if not patient:
            raise NotFoundException(f"Patient with id {data.patient_id} not found")
        if patient.role != RoleEnum.patient:
            raise BadRequestException(
                f"User with id {data.patient_id} is not a patient"
            )

        # Check if relationship already exists
        existing = (
            self.doctor_patient_relationship_repository.get_by_doctor_and_patient(
                data.doctor_id, data.patient_id
            )
        )
        if existing:
            raise ConflictException(
                "Relationship between this doctor and patient already exists"
            )

        relationship = DoctorPatientRelationship(
            doctor_id=data.doctor_id, patient_id=data.patient_id
        )
        created = self.doctor_patient_relationship_repository.create(relationship)
        logger.info(
            "Doctor-patient relationship created successfully",
            extra={
                "doctor_id": str(data.doctor_id),
                "patient_id": str(data.patient_id),
            },
        )
        return created

    def delete_doctor_patient_relationship(self, relationship_id: uuid.UUID) -> None:
        relationship = self.doctor_patient_relationship_repository.get_by_id(
            relationship_id
        )
        if not relationship:
            raise NotFoundException("Doctor-patient relationship not found")
        self.doctor_patient_relationship_repository.delete(relationship)
