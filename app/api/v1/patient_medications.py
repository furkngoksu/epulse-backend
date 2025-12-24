import uuid
from datetime import date
from fastapi import APIRouter, Depends, Query, status

from app.api.deps.auth import get_current_user, get_current_doctor
from app.api.deps.services import get_medication_service
from app.schemas.base import SuccessResponse
from app.schemas.patient_medication import (
    PatientMedicationResponse,
    PatientMedicationWithScheduleCreate,
)
from app.schemas.user import User
from app.services.medication_service import MedicationService

router = APIRouter(prefix="/patient-medications", tags=["PatientMedications"])


@router.post("/create/{patient_id}", response_model=SuccessResponse[PatientMedicationResponse], status_code=status.HTTP_201_CREATED)
def create_patient_medication_for_patient(
    patient_id: uuid.UUID,
    payload: PatientMedicationWithScheduleCreate,
    svc: MedicationService = Depends(get_medication_service),
    doctor: User = Depends(get_current_doctor),
) -> SuccessResponse[PatientMedicationResponse]:
    created = svc.create_patient_medication_with_schedule(
        patient_id=patient_id,
        data=payload)
    return SuccessResponse(content=created)


@router.get("/upcoming", response_model=SuccessResponse[list[PatientMedicationResponse]], status_code=status.HTTP_200_OK)
def list_upcoming_patient_medications(
    hours: int = Query(24, ge=1, le=168),
    svc: MedicationService = Depends(get_medication_service),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[list[PatientMedicationResponse]]:
    rows = svc.get_upcoming_patient_medications(patient_id=current_user.id, hours=hours)
    return SuccessResponse(content=rows)


@router.get("/between", response_model=SuccessResponse[list[PatientMedicationResponse]], status_code=status.HTTP_200_OK)
def list_patient_medications_between(
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


@router.get("", response_model=SuccessResponse[list[PatientMedicationResponse]], status_code=status.HTTP_200_OK)
def list_patient_medications(
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


@router.get("/{patient_medication_id}", response_model=SuccessResponse[PatientMedicationResponse], status_code=status.HTTP_200_OK)
def get_patient_medication(
    patient_medication_id: uuid.UUID,
    svc: MedicationService = Depends(get_medication_service),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[PatientMedicationResponse]:
    pm = svc.get_patient_medication(
        patient_medication_id=patient_medication_id,
        current_user_id=current_user.id,
    )
    return SuccessResponse(content=pm)


@router.delete("/{patient_medication_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient_medication(
    patient_medication_id: uuid.UUID,
    svc: MedicationService = Depends(get_medication_service),
    current_user: User = Depends(get_current_user),
):
    svc.delete_patient_medication(
        patient_medication_id=patient_medication_id,
        current_user_id=current_user.id,
    )
    return None
