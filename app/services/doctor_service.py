import uuid
from app.models.hospital import Hospital
from app.models.doctor_profile import DoctorProfile
from app.models.doctor_patient_relationship import DoctorPatientRelationship
from app.models.user import RoleEnum
from app.repositories.hospital import HospitalRepository
from app.repositories.doctor_profile_repository import DoctorProfileRepository
from app.repositories.doctor_patient_relationship import DoctorPatientRelationshipRepository
from app.repositories.user import UserRepository
from app.schemas.hospital import HospitalCreate, HospitalUpdate
from app.schemas.doctor_profile import DoctorProfileCreate, DoctorProfileUpdate
from app.schemas.doctor_patient_relationship import DoctorPatientRelationshipCreate
from app.exceptions.exceptions import NotFoundException, BadRequestException, ConflictException


class DoctorService:
    """
    Consolidated service for managing hospitals, doctor profiles, and doctor-patient relationships.
    """

    def __init__(
        self,
        hospital_repository: HospitalRepository,
        doctor_profile_repository: DoctorProfileRepository,
        doctor_patient_relationship_repository: DoctorPatientRelationshipRepository,
        user_repository: UserRepository
    ):
        self.hospital_repository = hospital_repository
        self.doctor_profile_repository = doctor_profile_repository
        self.doctor_patient_relationship_repository = doctor_patient_relationship_repository
        self.user_repository = user_repository

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
            phone=data.phone
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

    # ==================== Doctor Profile Methods ====================

    def get_all_doctor_profiles(self, skip: int = 0, limit: int = 100) -> list[DoctorProfile]:
        return self.doctor_profile_repository.get_all(skip=skip, limit=limit)

    def get_doctor_profile_by_id(self, profile_id: uuid.UUID) -> DoctorProfile:
        profile = self.doctor_profile_repository.get_by_id(profile_id)
        if not profile:
            raise NotFoundException("Doctor profile not found")
        return profile

    def get_doctors_by_hospital(self, hospital_id: uuid.UUID) -> list[DoctorProfile]:
        # Verify hospital exists
        hospital = self.hospital_repository.get_by_id(hospital_id)
        if not hospital:
            raise NotFoundException("Hospital not found")

        return self.doctor_profile_repository.get_by_hospital_id(hospital_id)

    def create_doctor_profile(self, data: DoctorProfileCreate) -> DoctorProfile:
        # Verify user exists and is a doctor
        user = self.user_repository.get_by_id(data.user_id)
        if not user:
            raise NotFoundException("User not found")

        if user.role != RoleEnum.doctor:
            raise BadRequestException("User must have doctor role")

        # Check if profile already exists for this user
        existing_profile = self.doctor_profile_repository.get_by_user_id(data.user_id)
        if existing_profile:
            raise ConflictException("Doctor profile already exists for this user")

        # Verify hospital exists
        hospital = self.hospital_repository.get_by_id(data.hospital_id)
        if not hospital:
            raise NotFoundException("Hospital not found")

        profile = DoctorProfile(
            id=data.user_id,
            hospital_id=data.hospital_id,
            specialty=data.specialty
        )
        return self.doctor_profile_repository.create(profile)

    def update_doctor_profile(self, profile_id: uuid.UUID, data: DoctorProfileUpdate) -> DoctorProfile:
        profile = self.doctor_profile_repository.get_by_id(profile_id)
        if not profile:
            raise NotFoundException("Doctor profile not found")

        # Update only provided fields
        if data.hospital_id is not None:
            # Verify hospital exists
            hospital = self.hospital_repository.get_by_id(data.hospital_id)
            if not hospital:
                raise NotFoundException("Hospital not found")
            profile.hospital_id = data.hospital_id

        if data.specialty is not None:
            profile.specialty = data.specialty

        return self.doctor_profile_repository.update(profile)

    def delete_doctor_profile(self, profile_id: uuid.UUID) -> None:
        profile = self.doctor_profile_repository.get_by_id(profile_id)
        if not profile:
            raise NotFoundException("Doctor profile not found")
        self.doctor_profile_repository.delete(profile)

    # ==================== Doctor-Patient Relationship Methods ====================

    def get_all_relationships(self, skip: int = 0, limit: int = 100) -> list[DoctorPatientRelationship]:
        return self.doctor_patient_relationship_repository.get_all(skip=skip, limit=limit)

    def get_relationship_by_id(self, relationship_id: uuid.UUID) -> DoctorPatientRelationship:
        relationship = self.doctor_patient_relationship_repository.get_by_id(relationship_id)
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

        return self.doctor_patient_relationship_repository.get_patients_for_doctor(doctor_id, skip, limit)

    def get_doctor_patient_summaries(
        self, doctor_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[dict]:
        """Get patient summaries with basic info for a specific doctor."""
        # Verify doctor exists and has doctor role
        doctor = self.user_repository.get_by_id(doctor_id)
        if not doctor:
            raise NotFoundException("Doctor not found")
        if doctor.role != RoleEnum.doctor:
            raise BadRequestException("User is not a doctor")

        return self.doctor_patient_relationship_repository.get_patient_summaries_for_doctor(doctor_id, skip, limit)

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

        return self.doctor_patient_relationship_repository.get_doctors_for_patient(patient_id, skip, limit)

    def create_doctor_patient_relationship(self, data: DoctorPatientRelationshipCreate) -> DoctorPatientRelationship:
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
            raise BadRequestException(f"User with id {data.patient_id} is not a patient")

        # Check if relationship already exists
        existing = self.doctor_patient_relationship_repository.get_by_doctor_and_patient(
            data.doctor_id, data.patient_id
        )
        if existing:
            raise ConflictException("Relationship between this doctor and patient already exists")

        relationship = DoctorPatientRelationship(
            doctor_id=data.doctor_id,
            patient_id=data.patient_id
        )
        return self.doctor_patient_relationship_repository.create(relationship)

    def delete_doctor_patient_relationship(self, relationship_id: uuid.UUID) -> None:
        relationship = self.doctor_patient_relationship_repository.get_by_id(relationship_id)
        if not relationship:
            raise NotFoundException("Doctor-patient relationship not found")
        self.doctor_patient_relationship_repository.delete(relationship)
