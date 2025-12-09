from sqlalchemy.orm import Session

from app.models.doctor_profile import DoctorProfile
from app.models.user import RoleEnum
from app.repositories.doctor_profile_repository import DoctorProfileRepository
from app.repositories.user import UserRepository
from app.repositories.hospital import HospitalRepository
from app.schemas.doctor_profile import DoctorProfileCreate, DoctorProfileUpdate
from app.exceptions.exceptions import NotFoundException, BadRequestException, ConflictException


class DoctorProfileService:

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[DoctorProfile]:
        return DoctorProfileRepository.get_all(db, skip=skip, limit=limit)

    @staticmethod
    def get_by_id(db: Session, profile_id: int) -> DoctorProfile:
        profile = DoctorProfileRepository.get_by_id(db, profile_id)
        if not profile:
            raise NotFoundException("Doctor profile not found")
        return profile

    @staticmethod
    def get_by_hospital_id(db: Session, hospital_id: int) -> list[DoctorProfile]:
        # Verify hospital exists
        hospital = HospitalRepository.get_by_id(db, hospital_id)
        if not hospital:
            raise NotFoundException("Hospital not found")

        return DoctorProfileRepository.get_by_hospital_id(db, hospital_id)

    @staticmethod
    def create(db: Session, data: DoctorProfileCreate) -> DoctorProfile:
        # Verify user exists and is a doctor
        user = UserRepository.get_by_id(db, data.user_id)
        if not user:
            raise NotFoundException("User not found")

        if user.role != RoleEnum.DOCTOR:
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
    def update(db: Session, profile_id: int, data: DoctorProfileUpdate) -> DoctorProfile:
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
    def delete(db: Session, profile_id: int) -> None:
        profile = DoctorProfileRepository.get_by_id(db, profile_id)
        if not profile:
            raise NotFoundException("Doctor profile not found")
        DoctorProfileRepository.delete(db, profile)
