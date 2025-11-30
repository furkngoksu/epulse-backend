from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps.db import get_db
from app.api.deps.auth import get_current_user, get_current_admin
from app.models.user import User
from app.schemas.doctor_profile import (
    DoctorProfileCreate,
    DoctorProfileUpdate,
    DoctorProfileResponse
)
from app.services.doctor_profile import DoctorProfileService

router = APIRouter()


@router.get("/", response_model=list[DoctorProfileResponse])
def get_doctor_profiles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all doctor profiles.
    Requires authentication.
    """
    profiles = DoctorProfileService.get_all(db, skip=skip, limit=limit)
    return profiles


@router.get("/hospital/{hospital_id}", response_model=list[DoctorProfileResponse])
def get_doctors_by_hospital(
    hospital_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all doctors at a specific hospital.
    Requires authentication.
    """
    profiles = DoctorProfileService.get_by_hospital_id(db, hospital_id)
    return profiles


@router.get("/{profile_id}", response_model=DoctorProfileResponse)
def get_doctor_profile(
    profile_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a doctor profile by ID.
    Requires authentication.
    """
    profile = DoctorProfileService.get_by_id(db, profile_id)
    return profile


@router.post("/", response_model=DoctorProfileResponse, status_code=201)
def create_doctor_profile(
    data: DoctorProfileCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Create a new doctor profile.
    Requires admin role.
    """
    profile = DoctorProfileService.create(db, data)
    return profile


@router.put("/{profile_id}", response_model=DoctorProfileResponse)
def update_doctor_profile(
    profile_id: UUID,
    data: DoctorProfileUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Update a doctor profile.
    Requires admin role.
    """
    profile = DoctorProfileService.update(db, profile_id, data)
    return profile


@router.delete("/{profile_id}", status_code=204)
def delete_doctor_profile(
    profile_id: UUID,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Delete a doctor profile.
    Requires admin role.
    """
    DoctorProfileService.delete(db, profile_id)
