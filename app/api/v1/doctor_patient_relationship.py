import uuid
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps.auth import get_current_user, get_current_admin
from app.schemas.user import User, RoleEnum
from app.schemas.doctor_patient_relationship import (
    DoctorPatientRelationshipCreate,
    DoctorPatientRelationshipResponse,
    PatientSummary
)
from app.services.doctor_service import DoctorService
from app.api.deps.services import get_doctor_service
from app.exceptions.exceptions import ForbiddenException

router = APIRouter()


@router.get("/", response_model=List[DoctorPatientRelationshipResponse], status_code=status.HTTP_200_OK)
def get_all_relationships(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    doctor_service: DoctorService = Depends(get_doctor_service),
    current_user: User = Depends(get_current_admin)
):
    """
    Get all doctor-patient relationships.
    Requires admin role.
    """
    relationships = doctor_service.get_all_relationships(skip=skip, limit=limit)
    return relationships


@router.get("/doctor/{doctor_id}/patients", response_model=List[PatientSummary], status_code=status.HTTP_200_OK)
def get_patients_for_doctor(
    doctor_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    doctor_service: DoctorService = Depends(get_doctor_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get all patients for a specific doctor with basic patient information.
    Doctors can only see their own patients. Admins can see any doctor's patients.
    Patients cannot access this endpoint.
    """
    # Only admins and doctors can access this endpoint
    if current_user.role == RoleEnum.patient:
        raise ForbiddenException("Patients cannot view doctor patient lists")

    # Doctors can only view their own patients, admins can view any
    if current_user.role == RoleEnum.doctor and current_user.id != doctor_id:
        raise ForbiddenException("You can only view your own patients")

    patient_summaries = doctor_service.get_doctor_patient_summaries(
        doctor_id, skip=skip, limit=limit
    )
    return patient_summaries


@router.get("/patient/{patient_id}/doctors", response_model=List[DoctorPatientRelationshipResponse], status_code=status.HTTP_200_OK)
def get_doctors_for_patient(
    patient_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    doctor_service: DoctorService = Depends(get_doctor_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get all doctors for a specific patient.
    Patients can only see their own doctors. Admins can see any patient's doctors.
    Doctors cannot access this endpoint.
    """
    # Only admins and patients can access this endpoint
    if current_user.role == RoleEnum.doctor:
        raise ForbiddenException("Doctors cannot view patient doctor lists")

    # Patients can only view their own doctors, admins can view any
    if current_user.role == RoleEnum.patient and current_user.id != patient_id:
        raise ForbiddenException("You can only view your own doctors")

    relationships = doctor_service.get_patient_doctors(
        patient_id, skip=skip, limit=limit
    )
    return relationships


@router.get("/{relationship_id}", response_model=DoctorPatientRelationshipResponse, status_code=status.HTTP_200_OK)
def get_relationship(
    relationship_id: uuid.UUID,
    doctor_service: DoctorService = Depends(get_doctor_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get a doctor-patient relationship by ID.
    Requires authentication.
    """
    relationship = doctor_service.get_relationship_by_id(relationship_id)
    return relationship


@router.post("/", response_model=DoctorPatientRelationshipResponse, status_code=status.HTTP_201_CREATED)
def create_relationship(
    data: DoctorPatientRelationshipCreate,
    doctor_service: DoctorService = Depends(get_doctor_service),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new doctor-patient relationship.
    Doctors can create relationships for themselves with patients.
    Admins can create any relationship.
    """
    # Doctors can only create relationships for themselves
    if current_user.role == RoleEnum.doctor and current_user.id != data.doctor_id:
        raise ForbiddenException("You can only create relationships for yourself")

    # Patients cannot create relationships
    if current_user.role == RoleEnum.patient:
        raise ForbiddenException("Patients cannot create doctor-patient relationships")

    relationship = doctor_service.create_doctor_patient_relationship(data)
    return relationship


@router.delete("/{relationship_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_relationship(
    relationship_id: uuid.UUID,
    doctor_service: DoctorService = Depends(get_doctor_service),
    current_user: User = Depends(get_current_admin)
):
    """
    Delete a doctor-patient relationship.
    Requires admin role.
    """
    doctor_service.delete_doctor_patient_relationship(relationship_id)
