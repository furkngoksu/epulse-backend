import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.deps.auth import (
    get_current_user,
    get_current_doctor,
    get_current_admin,
    get_current_patient,
)
from app.api.deps.services import get_prescription_service
from app.schemas.base import SuccessResponse
from app.schemas.user import User
from app.schemas.prescription import Prescription, PrescriptionCreate, PrescriptionUpdate
from app.schemas.prescription_item import PrescriptionItem, PrescriptionItemCreate, PrescriptionItemUpdate
from app.schemas.drug_interaction import DrugInteractionResponse
from app.services.prescription_service import PrescriptionService
from app.models.prescription import Status

router = APIRouter(prefix="/prescriptions", tags=["Prescriptions"])


@router.get("", response_model=SuccessResponse[list[Prescription]], status_code=status.HTTP_200_OK)
def admin_list_prescriptions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[Status] = Query(None),
    svc: PrescriptionService = Depends(get_prescription_service),
    admin: User = Depends(get_current_admin),
):
    data = svc.admin_list_prescriptions(skip=skip, limit=limit, status=status)
    return SuccessResponse(content=data)


@router.get("/doctor", response_model=SuccessResponse[list[Prescription]], status_code=status.HTTP_200_OK)
def doctor_list_prescriptions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[Status] = Query(None),
    svc: PrescriptionService = Depends(get_prescription_service),
    doctor: User = Depends(get_current_doctor),
):
    data = svc.doctor_list_prescriptions(doctor_id=doctor.id, skip=skip, limit=limit, status=status)
    return SuccessResponse(content=data)


@router.get("/patient", response_model=SuccessResponse[list[Prescription]], status_code=status.HTTP_200_OK)
def patient_list_prescriptions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[Status] = Query(None),
    svc: PrescriptionService = Depends(get_prescription_service),
    patient: User = Depends(get_current_patient),
):
    data = svc.patient_list_prescriptions(patient_id=patient.id, skip=skip, limit=limit, status=status)
    return SuccessResponse(content=data)


@router.post("", response_model=SuccessResponse[Prescription], status_code=status.HTTP_201_CREATED)
def create_prescription_doctor(
    payload: PrescriptionCreate,
    svc: PrescriptionService = Depends(get_prescription_service),
    current_doctor: User = Depends(get_current_doctor),
) -> SuccessResponse[Prescription]:
    created = svc.create_prescription(doctor_id=current_doctor.id, data=payload)
    return SuccessResponse(content=created)


@router.get("/{prescription_id}", response_model=SuccessResponse[Prescription], status_code=status.HTTP_200_OK)
def get_prescription(
    prescription_id: uuid.UUID,
    svc: PrescriptionService = Depends(get_prescription_service),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[Prescription]:
    rx = svc.get_prescription_by_id(prescription_id=prescription_id, current_user=current_user)
    return SuccessResponse(content=rx)


@router.patch("/{prescription_id}", response_model=SuccessResponse[Prescription], status_code=status.HTTP_200_OK)
def update_prescription(
    prescription_id: uuid.UUID,
    payload: PrescriptionUpdate,
    svc: PrescriptionService = Depends(get_prescription_service),
    current_doctor: User = Depends(get_current_doctor),  # şimdilik doctor only dedin
) -> SuccessResponse[Prescription]:
    updated = svc.update_prescription(prescription_id=prescription_id, data=payload, current_user=current_doctor)
    return SuccessResponse(content=updated)


@router.delete("/{prescription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prescription_doctor(
    prescription_id: uuid.UUID,
    svc: PrescriptionService = Depends(get_prescription_service),
    current_doctor: User = Depends(get_current_doctor),
):
    svc.delete_prescription(prescription_id=prescription_id, current_user=current_doctor)
    return None


# -------------------------
# Prescription Items
# -------------------------

@router.get("/{prescription_id}/items", response_model=SuccessResponse[list[PrescriptionItem]], status_code=status.HTTP_200_OK)
def list_prescription_items(
    prescription_id: uuid.UUID,
    svc: PrescriptionService = Depends(get_prescription_service),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[list[PrescriptionItem]]:
    items = svc.get_all_prescription_items(prescription_id=prescription_id, current_user=current_user)
    return SuccessResponse(content=items)


@router.post("/{prescription_id}/items", response_model=SuccessResponse[PrescriptionItem], status_code=status.HTTP_201_CREATED)
def add_item(
    prescription_id: uuid.UUID,
    payload: PrescriptionItemCreate,
    svc: PrescriptionService = Depends(get_prescription_service),
    current_doctor: User = Depends(get_current_doctor),  # şimdilik doctor only
) -> SuccessResponse[PrescriptionItem]:
    item = svc.add_prescription_item(prescription_id=prescription_id, data=payload, current_user=current_doctor)
    return SuccessResponse(content=item)


@router.post("/{prescription_id}/items/bulk", response_model=SuccessResponse[list[PrescriptionItem]], status_code=status.HTTP_201_CREATED)
def add_items_bulk(
    prescription_id: uuid.UUID,
    payload: list[PrescriptionItemCreate],
    svc: PrescriptionService = Depends(get_prescription_service),
    current_doctor: User = Depends(get_current_doctor),  # şimdilik doctor only
) -> SuccessResponse[list[PrescriptionItem]]:
    items = svc.add_prescription_items(prescription_id=prescription_id, items=payload, current_user=current_doctor)
    return SuccessResponse(content=items)


@router.patch("/items/{item_id}", response_model=SuccessResponse[PrescriptionItem], status_code=status.HTTP_200_OK)
def update_item(
    item_id: uuid.UUID,
    payload: PrescriptionItemUpdate,
    svc: PrescriptionService = Depends(get_prescription_service),
    current_doctor: User = Depends(get_current_doctor),
) -> SuccessResponse[PrescriptionItem]:
    updated = svc.update_prescription_item(item_id=item_id, data=payload, current_user=current_doctor)
    return SuccessResponse(content=updated)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: uuid.UUID,
    svc: PrescriptionService = Depends(get_prescription_service),
    current_doctor: User = Depends(get_current_doctor),
):
    svc.delete_prescription_item(item_id=item_id, current_user=current_doctor)
    return None


# -------------------------
# Interactions
# -------------------------

@router.get("/{prescription_id}/interactions", response_model=SuccessResponse[list[DrugInteractionResponse]], status_code=status.HTTP_200_OK)
def check_prescription_interactions(
    prescription_id: uuid.UUID,
    svc: PrescriptionService = Depends(get_prescription_service),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[list[DrugInteractionResponse]]:
    rows = svc.check_prescription_interactions(prescription_id=prescription_id, current_user=current_user)
    return SuccessResponse(content=rows)
