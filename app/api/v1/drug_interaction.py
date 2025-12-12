import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps.services import get_catalog_service
from app.api.deps.auth import get_current_user, get_current_admin
from app.schemas.user import User
from app.schemas.drug_interaction import (
    DrugInteractionCreate,
    DrugInteractionUpdate,
    DrugInteractionResponse
)
from app.services.catalog_service import CatalogService

router = APIRouter()


@router.get("/", response_model=list[DrugInteractionResponse])
def get_drug_interactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    catalog_service: CatalogService = Depends(get_catalog_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get all drug interactions.
    Requires authentication.
    """
    interactions = catalog_service.get_all_interactions(skip=skip, limit=limit)
    return interactions


@router.get("/check", response_model=DrugInteractionResponse | None)
def check_drug_interaction(
    medication_id_1: uuid.UUID = Query(...),
    medication_id_2: uuid.UUID = Query(...),
    catalog_service: CatalogService = Depends(get_catalog_service),
    current_user: User = Depends(get_current_user)
):
    """
    Check if there's an interaction between two medications.
    Returns the interaction if found, null otherwise.
    Requires authentication.
    """
    interaction = catalog_service.check_drug_interaction(medication_id_1, medication_id_2)
    return interaction


@router.get("/medication/{medication_id}", response_model=list[DrugInteractionResponse])
def get_interactions_for_medication(
    medication_id: uuid.UUID,
    catalog_service: CatalogService = Depends(get_catalog_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get all interactions for a specific medication.
    Requires authentication.
    """
    interactions = catalog_service.get_medication_interactions(medication_id)
    return interactions


@router.get("/{interaction_id}", response_model=DrugInteractionResponse)
def get_drug_interaction(
    interaction_id: uuid.UUID,
    catalog_service: CatalogService = Depends(get_catalog_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get a drug interaction by ID.
    Requires authentication.
    """
    interaction = catalog_service.get_interaction_by_id(interaction_id)
    return interaction


@router.post("/", response_model=DrugInteractionResponse, status_code=201)
def create_drug_interaction(
    data: DrugInteractionCreate,
    catalog_service: CatalogService = Depends(get_catalog_service),
    current_admin: User = Depends(get_current_admin)
):
    """
    Create a new drug interaction.
    Requires admin role.
    """
    interaction = catalog_service.create_interaction(data)
    return interaction


@router.put("/{interaction_id}", response_model=DrugInteractionResponse)
def update_drug_interaction(
    interaction_id: uuid.UUID,
    data: DrugInteractionUpdate,
    catalog_service: CatalogService = Depends(get_catalog_service),
    current_admin: User = Depends(get_current_admin)
):
    """
    Update a drug interaction.
    Requires admin role.
    """
    interaction = catalog_service.update_interaction(interaction_id, data)
    return interaction


@router.delete("/{interaction_id}", status_code=204)
def delete_drug_interaction(
    interaction_id: uuid.UUID,
    catalog_service: CatalogService = Depends(get_catalog_service),
    current_admin: User = Depends(get_current_admin)
):
    """
    Delete a drug interaction.
    Requires admin role.
    """
    catalog_service.delete_interaction(interaction_id)
