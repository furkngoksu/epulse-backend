import uuid
from fastapi import APIRouter, Depends, Query

from app.api.deps.auth import get_current_user, get_current_admin
from app.api.deps.services import get_doctor_service
from app.schemas.user import User
from app.schemas.hospital import HospitalCreate, HospitalUpdate, HospitalResponse
from app.services.doctor_service import DoctorService

router = APIRouter()


@router.get("/", response_model=list[HospitalResponse])
def get_hospitals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: DoctorService = Depends(get_doctor_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get all hospitals.
    Requires authentication.
    """
    hospitals = service.get_all_hospitals(skip=skip, limit=limit)
    return hospitals


@router.get("/{hospital_id}", response_model=HospitalResponse)
def get_hospital(
    hospital_id: uuid.UUID,
    service: DoctorService = Depends(get_doctor_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get a hospital by ID.
    Requires authentication.
    """
    hospital = service.get_hospital_by_id(hospital_id)
    return hospital


@router.post("/", response_model=HospitalResponse, status_code=201)
def create_hospital(
    data: HospitalCreate,
    service: DoctorService = Depends(get_doctor_service),
    current_admin: User = Depends(get_current_admin)
):
    """
    Create a new hospital.
    Requires admin role.
    """
    hospital = service.create_hospital(data)
    return hospital


@router.put("/{hospital_id}", response_model=HospitalResponse)
def update_hospital(
    hospital_id: uuid.UUID,
    data: HospitalUpdate,
    service: DoctorService = Depends(get_doctor_service),
    current_admin: User = Depends(get_current_admin)
):
    """
    Update a hospital.
    Requires admin role.
    """
    hospital = service.update_hospital(hospital_id, data)
    return hospital


@router.delete("/{hospital_id}", status_code=204)
def delete_hospital(
    hospital_id: uuid.UUID,
    service: DoctorService = Depends(get_doctor_service),
    current_admin: User = Depends(get_current_admin)
):
    """
    Delete a hospital.
    Requires admin role.
    """
    service.delete_hospital(hospital_id)
