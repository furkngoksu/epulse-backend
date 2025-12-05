from sqlalchemy.orm import Session

from app.models.hospital import Hospital
from app.models.doctor_profile import DoctorProfile
from app.models.doctor_patient_relationship import DoctorPatientRelationship
from app.models.user import RoleEnum
from app.repositories.hospital import HospitalRepository
from app.repositories.doctor_profile import DoctorProfileRepository
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

    # ==================== Hospital Methods ====================

    @staticmethod
    def get_all_hospitals(db: Session, skip: int = 0, limit: int = 100) -> list[Hospital]:
        return HospitalRepository.get_all(db, skip=skip, limit=limit)

    @staticmethod
    def get_hospital_by_id(db: Session, hospital_id: int) -> Hospital:
        hospital = HospitalRepository.get_by_id(db, hospital_id)
        if not hospital:
            raise NotFoundException("Hospital not found")
        return hospital

    @staticmethod
    def create_hospital(db: Session, data: HospitalCreate) -> Hospital:
        hospital = Hospital(
            name=data.name,
            address=data.address,
            city=data.city,
            district=data.district,
            phone=data.phone
        )
        return HospitalRepository.create(db, hospital)

    @staticmethod
    def update_hospital(db: Session, hospital_id: int, data: HospitalUpdate) -> Hospital:
        hospital = HospitalRepository.get_by_id(db, hospital_id)
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

        return HospitalRepository.update(db, hospital)

    @staticmethod
    def delete_hospital(db: Session, hospital_id: int) -> None:
        hospital = HospitalRepository.get_by_id(db, hospital_id)
        if not hospital:
            raise NotFoundException("Hospital not found")
        HospitalRepository.delete(db, hospital)

    # ==================== Doctor Profile Methods ====================

    @staticmethod
    def get_all_doctor_profiles(db: Session, skip: int = 0, limit: int = 100) -> list[DoctorProfile]:
        return DoctorProfileRepository.get_all(db, skip=skip, limit=limit)

    @staticmethod
    def get_doctor_profile_by_id(db: Session, profile_id: int) -> DoctorProfile:
        profile = DoctorProfileRepository.get_by_id(db, profile_id)
        if not profile:
            raise NotFoundException("Doctor profile not found")
        return profile

    @staticmethod
    def get_doctors_by_hospital(db: Session, hospital_id: int) -> list[DoctorProfile]:
        # Verify hospital exists
        hospital = HospitalRepository.get_by_id(db, hospital_id)
        if not hospital:
            raise NotFoundException("Hospital not found")

        return DoctorProfileRepository.get_by_hospital_id(db, hospital_id)

    @staticmethod
    def create_doctor_profile(db: Session, data: DoctorProfileCreate) -> DoctorProfile:
        # Verify user exists and is a doctor
        user = UserRepository.get_by_id(db, data.user_id)
        if not user:
            raise NotFoundException("User not found")

        if user.role != RoleEnum.doctor:
            raise BadRequestException("User must have doctor role")

        # Check if profile already exists for this user
        existing_profile = DoctorProfileRepository.get_by_user_id(db, data.user_id)
        if existing_profile:
            raise ConflictException("Doctor profile already exists for this user")

        # Verify hospital exists
        hospital = HospitalRepository.get_by_id(db, data.hospital_id)
        if not hospital:
            raise NotFoundException("Hospital not found")

        profile = DoctorProfile(
            id=data.user_id,
            hospital_id=data.hospital_id,
            specialty=data.specialty
        )
        return DoctorProfileRepository.create(db, profile)

    @staticmethod
    def update_doctor_profile(db: Session, profile_id: int, data: DoctorProfileUpdate) -> DoctorProfile:
        profile = DoctorProfileRepository.get_by_id(db, profile_id)
        if not profile:
            raise NotFoundException("Doctor profile not found")

        # Update only provided fields
        if data.hospital_id is not None:
            # Verify hospital exists
            hospital = HospitalRepository.get_by_id(db, data.hospital_id)
            if not hospital:
                raise NotFoundException("Hospital not found")
            profile.hospital_id = data.hospital_id

        if data.specialty is not None:
            profile.specialty = data.specialty

        return DoctorProfileRepository.update(db, profile)

    @staticmethod
    def delete_doctor_profile(db: Session, profile_id: int) -> None:
        profile = DoctorProfileRepository.get_by_id(db, profile_id)
        if not profile:
            raise NotFoundException("Doctor profile not found")
        DoctorProfileRepository.delete(db, profile)

    # ==================== Doctor-Patient Relationship Methods ====================

    @staticmethod
    def get_all_relationships(db: Session, skip: int = 0, limit: int = 100) -> list[DoctorPatientRelationship]:
        return DoctorPatientRelationshipRepository.get_all(db, skip=skip, limit=limit)

    @staticmethod
    def get_relationship_by_id(db: Session, relationship_id: int) -> DoctorPatientRelationship:
        relationship = DoctorPatientRelationshipRepository.get_by_id(db, relationship_id)
        if not relationship:
            raise NotFoundException("Doctor-patient relationship not found")
        return relationship

    @staticmethod
    def get_doctor_patients(
        db: Session, doctor_id: int, skip: int = 0, limit: int = 100
    ) -> list[DoctorPatientRelationship]:
        """Get all patients for a specific doctor."""
        # Verify doctor exists and has doctor role
        doctor = UserRepository.get_by_id(db, doctor_id)
        if not doctor:
            raise NotFoundException("Doctor not found")
        if doctor.role != RoleEnum.doctor:
            raise BadRequestException("User is not a doctor")

        return DoctorPatientRelationshipRepository.get_patients_for_doctor(db, doctor_id, skip, limit)

    @staticmethod
    def get_patient_doctors(
        db: Session, patient_id: int, skip: int = 0, limit: int = 100
    ) -> list[DoctorPatientRelationship]:
        """Get all doctors for a specific patient."""
        # Verify patient exists and has patient role
        patient = UserRepository.get_by_id(db, patient_id)
        if not patient:
            raise NotFoundException("Patient not found")
        if patient.role != RoleEnum.patient:
            raise BadRequestException("User is not a patient")

        return DoctorPatientRelationshipRepository.get_doctors_for_patient(db, patient_id, skip, limit)

    @staticmethod
    def create_doctor_patient_relationship(db: Session, data: DoctorPatientRelationshipCreate) -> DoctorPatientRelationship:
        # Validate doctor exists and has doctor role
        doctor = UserRepository.get_by_id(db, data.doctor_id)
        if not doctor:
            raise NotFoundException(f"Doctor with id {data.doctor_id} not found")
        if doctor.role != RoleEnum.doctor:
            raise BadRequestException(f"User with id {data.doctor_id} is not a doctor")

        # Validate patient exists and has patient role
        patient = UserRepository.get_by_id(db, data.patient_id)
        if not patient:
            raise NotFoundException(f"Patient with id {data.patient_id} not found")
        if patient.role != RoleEnum.patient:
            raise BadRequestException(f"User with id {data.patient_id} is not a patient")

        # Check if relationship already exists
        existing = DoctorPatientRelationshipRepository.get_by_doctor_and_patient(
            db, data.doctor_id, data.patient_id
        )
        if existing:
            raise ConflictException("Relationship between this doctor and patient already exists")

        relationship = DoctorPatientRelationship(
            doctor_id=data.doctor_id,
            patient_id=data.patient_id
        )
        return DoctorPatientRelationshipRepository.create(db, relationship)

    @staticmethod
    def delete_doctor_patient_relationship(db: Session, relationship_id: int) -> None:
        relationship = DoctorPatientRelationshipRepository.get_by_id(db, relationship_id)
        if not relationship:
            raise NotFoundException("Doctor-patient relationship not found")
        DoctorPatientRelationshipRepository.delete(db, relationship)
