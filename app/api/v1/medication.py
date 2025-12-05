from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps.db import get_db
from app.api.deps.auth import get_current_user, get_current_admin
from app.schemas.user import User
from app.schemas.medication import MedicationCreate, MedicationUpdate, MedicationResponse
from app.services.catalog_service import CatalogService

router = APIRouter()


@router.get("/", response_model=list[MedicationResponse])
def get_medications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all medications.
    Requires authentication.
    """
    medications = CatalogService.get_all_medications(db, skip=skip, limit=limit)
    return medications


@router.get("/search", response_model=list[MedicationResponse])
def search_medications(
    name: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search medications by commercial name.
    Requires authentication.
    """
    medications = CatalogService.search_medications(db, name, skip=skip, limit=limit)
    return medications


@router.get("/{medication_id}", response_model=MedicationResponse)
def get_medication(
    medication_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a medication by ID.
    Requires authentication.
    """
    medication = CatalogService.get_medication_by_id(db, medication_id)
    return medication


@router.post("/", response_model=MedicationResponse, status_code=201)
def create_medication(
    data: MedicationCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Create a new medication.
    Requires admin role.
    """
    medication = CatalogService.create_medication(db, data)
    return medication


@router.put("/{medication_id}", response_model=MedicationResponse)
def update_medication(
    medication_id: int,
    data: MedicationUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Update a medication.
    Requires admin role.
    """
    medication = CatalogService.update_medication(db, medication_id, data)
    return medication


@router.delete("/{medication_id}", status_code=204)
def delete_medication(
    medication_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Delete a medication.
    Requires admin role.
    """
    CatalogService.delete_medication(db, medication_id)
