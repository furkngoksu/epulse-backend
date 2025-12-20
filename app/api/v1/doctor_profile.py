import uuid
from fastapi import APIRouter, Depends, Query

from app.api.deps.auth import get_current_user, get_current_admin
from app.api.deps.services import get_doctor_service
from app.schemas.user import User
from app.schemas.doctor_profile import (
    DoctorProfileCreate,
    DoctorProfileUpdate,
    DoctorProfileResponse
)
from app.services.doctor_service import DoctorService

router = APIRouter()


@router.get("/", response_model=list[DoctorProfileResponse])
def get_doctor_profiles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: DoctorService = Depends(get_doctor_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get all doctor profiles.
    Requires authentication.
    """
    profiles = service.get_all_doctor_profiles(skip=skip, limit=limit)
    return profiles


@router.get("/clinic/{clinic_id}", response_model=list[DoctorProfileResponse])
def get_doctors_by_clinic(
    clinic_id: uuid.UUID,
    service: DoctorService = Depends(get_doctor_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get all doctors at a specific hospital.
    Requires authentication.
    """
    profiles = service.get_doctors_by_clinic(clinic_id)
    return profiles


@router.get("/{profile_id}", response_model=DoctorProfileResponse)
def get_doctor_profile(
    profile_id: uuid.UUID,
    service: DoctorService = Depends(get_doctor_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get a doctor profile by ID.
    Requires authentication.
    """
    profile = service.get_doctor_profile_by_id(profile_id)
    return profile


@router.post("/", response_model=DoctorProfileResponse, status_code=201)
def create_doctor_profile(
    data: DoctorProfileCreate,
    service: DoctorService = Depends(get_doctor_service),
    current_admin: User = Depends(get_current_admin)
):
    """
    Create a new doctor profile.
    Requires admin role.
    """
    profile = service.create_doctor_profile(data)
    return profile


@router.put("/{profile_id}", response_model=DoctorProfileResponse)
def update_doctor_profile(
    profile_id: uuid.UUID,
    data: DoctorProfileUpdate,
    service: DoctorService = Depends(get_doctor_service),
    current_admin: User = Depends(get_current_admin)
):
    """
    Update a doctor profile.
    Requires admin role.
    """
    profile = service.update_doctor_profile(profile_id, data)
    return profile


@router.delete("/{profile_id}", status_code=204)
def delete_doctor_profile(
    profile_id: uuid.UUID,
    service: DoctorService = Depends(get_doctor_service),
    current_admin: User = Depends(get_current_admin)
):
    """
    Delete a doctor profile.
    Requires admin role.
    """
    service.delete_doctor_profile(profile_id)
