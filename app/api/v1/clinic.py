import uuid
from fastapi import APIRouter, Depends, Query

from app.api.deps.auth import get_current_user, get_current_admin
from app.api.deps.services import get_doctor_service
from app.schemas.user import User
from app.schemas.clinic import ClinicCreate, ClinicUpdate, ClinicResponse
from app.services.doctor_service import DoctorService

router = APIRouter()


@router.get("/", response_model=list[ClinicResponse])
def get_clinics(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: DoctorService = Depends(get_doctor_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get all clinics.
    Requires authentication.
    """
    clinics = service.get_all_clinics(skip=skip, limit=limit)
    return clinics


@router.get("/{clinic_id}", response_model=ClinicResponse)
def get_clinic(
    clinic_id: uuid.UUID,
    service: DoctorService = Depends(get_doctor_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get a clinic by ID.
    Requires authentication.
    """
    clinic = service.get_clinic_by_id(clinic_id)
    return clinic


@router.post("/", response_model=ClinicResponse, status_code=201)
def create_clinic(
    data: ClinicCreate,
    service: DoctorService = Depends(get_doctor_service),
    current_admin: User = Depends(get_current_admin)
):
    """
    Create a new clinic.
    Requires admin role.
    """
    clinic = service.create_clinic(data)
    return clinic


@router.put("/{clinic_id}", response_model=ClinicResponse)
def update_clinic(
    clinic_id: uuid.UUID,
    data: ClinicUpdate,
    service: DoctorService = Depends(get_doctor_service),
    current_admin: User = Depends(get_current_admin)
):
    """
    Update a clinic.
    Requires admin role.
    """
    clinic = service.update_clinic(clinic_id, data)
    return clinic


@router.delete("/{clinic_id}", status_code=204)
def delete_clinic(
    clinic_id: uuid.UUID,
    service: DoctorService = Depends(get_doctor_service),
    current_admin: User = Depends(get_current_admin)
):
    """
    Delete a clinic.
    Requires admin role.
    """
    service.delete_clinic(clinic_id)
