import uuid
from fastapi import APIRouter, Depends, status

from app.api.deps.auth import get_current_patient
from app.api.deps.services import get_medication_service
from app.schemas.base import SuccessResponse
from app.schemas.medication_alias import MedicationAliasCreate, MedicationAliasResponse
from app.schemas.user import User
from app.services.medication_service import MedicationService

router = APIRouter(prefix="/medications", tags=["medication-alias"])


@router.post("/alias", response_model=SuccessResponse[MedicationAliasResponse], status_code=status.HTTP_201_CREATED)
def set_medication_alias(
    data: MedicationAliasCreate,
    svc: MedicationService = Depends(get_medication_service),
    patient: User = Depends(get_current_patient),
) -> SuccessResponse[MedicationAliasResponse]:
    alias = svc.set_alias(
        user_id=patient.id,
        medication_id=data.medication_id,
        alias_name=data.alias_name,
    )
    return SuccessResponse(content=alias)


@router.get("/aliases", response_model=SuccessResponse[list[MedicationAliasResponse]], status_code=status.HTTP_200_OK)
def get_medication_aliases(
    svc: MedicationService = Depends(get_medication_service),
    patient: User = Depends(get_current_patient),
) -> SuccessResponse[list[MedicationAliasResponse]]:
    aliases = svc.get_aliases(user_id=patient.id)
    return SuccessResponse(content=aliases)


@router.delete("/alias/{alias_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medication_alias(
    alias_id: uuid.UUID,
    svc: MedicationService = Depends(get_medication_service),
    patient: User = Depends(get_current_patient),
):
    svc.delete_alias(alias_id=alias_id, user_id=patient.id)
    return None
