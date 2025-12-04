from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps.db import get_db
from app.api.deps.auth import get_current_user, get_current_admin
from app.models.user import User
from app.schemas.drug_interaction import (
    DrugInteractionCreate,
    DrugInteractionUpdate,
    DrugInteractionResponse
)
from app.services.drug_interaction import DrugInteractionService

router = APIRouter()


@router.get("/", response_model=list[DrugInteractionResponse])
def get_drug_interactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all drug interactions.
    Requires authentication.
    """
    interactions = DrugInteractionService.get_all(db, skip=skip, limit=limit)
    return interactions


@router.get("/check", response_model=DrugInteractionResponse | None)
def check_drug_interaction(
    medication_id_1: int = Query(..., gt=0),
    medication_id_2: int = Query(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check if there's an interaction between two medications.
    Returns the interaction if found, null otherwise.
    Requires authentication.
    """
    interaction = DrugInteractionService.check_interaction(db, medication_id_1, medication_id_2)
    return interaction


@router.get("/medication/{medication_id}", response_model=list[DrugInteractionResponse])
def get_interactions_for_medication(
    medication_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all interactions for a specific medication.
    Requires authentication.
    """
    interactions = DrugInteractionService.get_interactions_for_medication(db, medication_id)
    return interactions


@router.get("/{interaction_id}", response_model=DrugInteractionResponse)
def get_drug_interaction(
    interaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a drug interaction by ID.
    Requires authentication.
    """
    interaction = DrugInteractionService.get_by_id(db, interaction_id)
    return interaction


@router.post("/", response_model=DrugInteractionResponse, status_code=201)
def create_drug_interaction(
    data: DrugInteractionCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Create a new drug interaction.
    Requires admin role.
    """
    interaction = DrugInteractionService.create(db, data)
    return interaction


@router.put("/{interaction_id}", response_model=DrugInteractionResponse)
def update_drug_interaction(
    interaction_id: int,
    data: DrugInteractionUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Update a drug interaction.
    Requires admin role.
    """
    interaction = DrugInteractionService.update(db, interaction_id, data)
    return interaction


@router.delete("/{interaction_id}", status_code=204)
def delete_drug_interaction(
    interaction_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Delete a drug interaction.
    Requires admin role.
    """
    DrugInteractionService.delete(db, interaction_id)
