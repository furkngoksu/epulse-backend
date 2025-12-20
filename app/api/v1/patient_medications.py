import uuid
from datetime import date
from fastapi import APIRouter, Depends, Query

from app.api.deps.auth import get_current_user
from app.api.deps.services import get_medication_service
from app.schemas.base import SuccessResponse
from app.schemas.patient_medication import (
    PatientMedicationResponse,
    PatientMedicationWithScheduleCreate,
    PatientMedicationCreatedResponse,
)
from app.schemas.user import User
from app.services.medication_service import MedicationService

router = APIRouter(prefix="/me/patient-medications", tags=["PatientMedications"])


@router.post("", response_model=SuccessResponse[PatientMedicationCreatedResponse], status_code=201)
def create_my_patient_medication(
    payload: PatientMedicationWithScheduleCreate,
    svc: MedicationService = Depends(get_medication_service),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[PatientMedicationCreatedResponse]:
    created = svc.create_patient_medication_with_schedule(
        current_user_id=current_user.id,
        data=payload,
    )
    return SuccessResponse(content=created)


@router.get("/upcoming", response_model=SuccessResponse[list[PatientMedicationResponse]])
def get_upcoming(
    hours: int = Query(24, ge=1, le=168),
    svc: MedicationService = Depends(get_medication_service),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[list[PatientMedicationResponse]]:
    rows = svc.get_upcoming_patient_medications(patient_id=current_user.id, hours=hours)
    return SuccessResponse(content=rows)


@router.get("/between", response_model=SuccessResponse[list[PatientMedicationResponse]])
def get_between(
    start: date = Query(...),
    end: date = Query(...),
    svc: MedicationService = Depends(get_medication_service),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[list[PatientMedicationResponse]]:
    rows = svc.get_patient_medications_between(
        patient_id=current_user.id,
        range_start=start,
        range_end=end,
    )
    return SuccessResponse(content=rows)


@router.get("", response_model=SuccessResponse[list[PatientMedicationResponse]])
def list_my_patient_medications(
    status: str = Query("all", pattern="^(active|paused|all)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    svc: MedicationService = Depends(get_medication_service),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[list[PatientMedicationResponse]]:
    rows = svc.list_patient_medications(
        user_id=current_user.id,
        status=status,
        skip=skip,
        limit=limit,
    )
    return SuccessResponse(content=rows)


@router.get("/{patient_medication_id}", response_model=SuccessResponse[PatientMedicationResponse])
def get_my_patient_medication(
    patient_medication_id: uuid.UUID,
    svc: MedicationService = Depends(get_medication_service),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[PatientMedicationResponse]:
    pm = svc.get_patient_medication(patient_medication_id)

    # ownership check burada da olur ama idealde service’de ayrı method ile yapılır.
    if pm.user_id != current_user.id:
        from app.exceptions.exceptions import ForbiddenException
        raise ForbiddenException("You do not have access to this patient medication")

    return SuccessResponse(content=pm)


@router.delete("/{patient_medication_id}", response_model=SuccessResponse[dict])
def delete_my_patient_medication(
    patient_medication_id: uuid.UUID,
    svc: MedicationService = Depends(get_medication_service),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[dict]:
    pm = svc.get_patient_medication(patient_medication_id)
    if pm.user_id != current_user.id:
        from app.exceptions.exceptions import ForbiddenException
        raise ForbiddenException("You do not have access to this patient medication")

    svc.delete_patient_medication(patient_medication_id)
    return SuccessResponse(content={"deleted": True})
