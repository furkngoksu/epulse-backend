import uuid
from fastapi import APIRouter, Depends, Query, status

from app.api.deps.services import get_catalog_service
from app.schemas.drug_interaction import (
    DrugInteractionCreate,
    DrugInteractionUpdate,
    DrugInteractionResponse,
)
from app.api.deps.auth import get_current_user, get_current_admin
from app.schemas.base import SuccessResponse
from app.schemas.user import User
from app.schemas.medication import (
    MedicationCreate,
    MedicationUpdate,
    MedicationResponse,
)
from app.services.catalog_service import CatalogService

router = APIRouter()


@router.get(
    "/medications",
    response_model=SuccessResponse[list[MedicationResponse]],
    status_code=status.HTTP_200_OK,
)
def list_medications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    q: str | None = Query(None, min_length=1),
    svc: CatalogService = Depends(get_catalog_service),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[list[MedicationResponse]]:
    rows = svc.list_medications(skip=skip, limit=limit, query=q)
    return SuccessResponse(content=rows)


@router.get(
    "/medications/{medication_id}",
    response_model=SuccessResponse[MedicationResponse],
    status_code=status.HTTP_200_OK,
)
def get_medication(
    medication_id: uuid.UUID,
    svc: CatalogService = Depends(get_catalog_service),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[MedicationResponse]:
    row = svc.get_medication_by_id(medication_id)
    return SuccessResponse(content=row)


# -------------------------
# Medications (Admin)
# -------------------------


@router.post(
    "/medications",
    response_model=SuccessResponse[MedicationResponse],
    status_code=status.HTTP_201_CREATED,
)
def create_medication(
    payload: MedicationCreate,
    svc: CatalogService = Depends(get_catalog_service),
    current_admin: User = Depends(get_current_admin),
) -> SuccessResponse[MedicationResponse]:
    row = svc.create_medication(payload)
    return SuccessResponse(content=row)


@router.patch(
    "/medications/{medication_id}",
    response_model=SuccessResponse[MedicationResponse],
    status_code=status.HTTP_200_OK,
)
def update_medication(
    medication_id: uuid.UUID,
    payload: MedicationUpdate,
    svc: CatalogService = Depends(get_catalog_service),
    current_admin: User = Depends(get_current_admin),
) -> SuccessResponse[MedicationResponse]:
    row = svc.update_medication(medication_id, payload)
    return SuccessResponse(content=row)


@router.delete("/medications/{medication_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medication(
    medication_id: uuid.UUID,
    svc: CatalogService = Depends(get_catalog_service),
    current_admin: User = Depends(get_current_admin),
):
    svc.delete_medication(medication_id)
    return None


# -------------------------
# Drug Interactions (User)
# -------------------------


@router.get(
    "/drug-interactions/check",
    response_model=SuccessResponse[DrugInteractionResponse | None],
    status_code=status.HTTP_200_OK,
)
def check_interaction(
    med_id_1: uuid.UUID = Query(...),
    med_id_2: uuid.UUID = Query(...),
    svc: CatalogService = Depends(get_catalog_service),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[DrugInteractionResponse | None]:
    row = svc.check_interaction(med_id_1, med_id_2)
    return SuccessResponse(content=row)


@router.get(
    "/drug-interactions/for-medication/{medication_id}",
    response_model=SuccessResponse[list[DrugInteractionResponse]],
    status_code=status.HTTP_200_OK,
)
def get_interactions_for_medication(
    medication_id: uuid.UUID,
    svc: CatalogService = Depends(get_catalog_service),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[list[DrugInteractionResponse]]:
    rows = svc.get_interactions_for_medication(medication_id)
    return SuccessResponse(content=rows)


# -------------------------
# Drug Interactions (Admin)
# -------------------------


@router.get(
    "/drug-interactions",
    response_model=SuccessResponse[list[DrugInteractionResponse]],
    status_code=status.HTTP_200_OK,
)
def get_all_interactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    svc: CatalogService = Depends(get_catalog_service),
    current_admin: User = Depends(get_current_admin),
) -> SuccessResponse[list[DrugInteractionResponse]]:
    rows = svc.get_all_interactions(skip=skip, limit=limit)
    return SuccessResponse(content=rows)


@router.get(
    "/drug-interactions/{interaction_id}",
    response_model=SuccessResponse[DrugInteractionResponse],
    status_code=status.HTTP_200_OK,
)
def get_interaction(
    interaction_id: uuid.UUID,
    svc: CatalogService = Depends(get_catalog_service),
    current_admin: User = Depends(get_current_admin),
) -> SuccessResponse[DrugInteractionResponse]:
    row = svc.get_interaction_by_id(interaction_id)
    return SuccessResponse(content=row)


@router.post(
    "/drug-interactions",
    response_model=SuccessResponse[DrugInteractionResponse],
    status_code=status.HTTP_201_CREATED,
)
def create_interaction(
    payload: DrugInteractionCreate,
    svc: CatalogService = Depends(get_catalog_service),
    current_admin: User = Depends(get_current_admin),
) -> SuccessResponse[DrugInteractionResponse]:
    row = svc.create_interaction(payload)
    return SuccessResponse(content=row)


@router.patch(
    "/drug-interactions/{interaction_id}",
    response_model=SuccessResponse[DrugInteractionResponse],
    status_code=status.HTTP_200_OK,
)
def update_interaction(
    interaction_id: uuid.UUID,
    payload: DrugInteractionUpdate,
    svc: CatalogService = Depends(get_catalog_service),
    current_admin: User = Depends(get_current_admin),
) -> SuccessResponse[DrugInteractionResponse]:
    row = svc.update_interaction(interaction_id, payload)
    return SuccessResponse(content=row)


@router.delete(
    "/drug-interactions/{interaction_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_interaction(
    interaction_id: uuid.UUID,
    svc: CatalogService = Depends(get_catalog_service),
    current_admin: User = Depends(get_current_admin),
):
    svc.delete_interaction(interaction_id)
    return None
