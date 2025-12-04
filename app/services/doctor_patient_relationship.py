from sqlalchemy.orm import Session

from app.models.doctor_patient_relationship import DoctorPatientRelationship
from app.models.user import RoleEnum
from app.repositories.doctor_patient_relationship import DoctorPatientRelationshipRepository
from app.repositories.user import UserRepository
from app.schemas.doctor_patient_relationship import DoctorPatientRelationshipCreate
from app.exceptions.exceptions import NotFoundException, BadRequestException, ConflictException


class DoctorPatientRelationshipService:

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[DoctorPatientRelationship]:
        return DoctorPatientRelationshipRepository.get_all(db, skip=skip, limit=limit)

    @staticmethod
    def get_by_id(db: Session, relationship_id: int) -> DoctorPatientRelationship:
        relationship = DoctorPatientRelationshipRepository.get_by_id(db, relationship_id)
        if not relationship:
            raise NotFoundException("Doctor-patient relationship not found")
        return relationship

    @staticmethod
    def get_patients_for_doctor(
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
    def get_doctors_for_patient(
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
    def create(db: Session, data: DoctorPatientRelationshipCreate) -> DoctorPatientRelationship:
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
    def delete(db: Session, relationship_id: int) -> None:
        relationship = DoctorPatientRelationshipRepository.get_by_id(db, relationship_id)
        if not relationship:
            raise NotFoundException("Doctor-patient relationship not found")
        DoctorPatientRelationshipRepository.delete(db, relationship)
