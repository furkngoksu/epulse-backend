import uuid
from fastapi import APIRouter, Depends, Query

from app.api.deps.auth import get_current_user, get_current_doctor_or_admin
from app.api.deps.services import get_prescription_service
from app.exceptions.exceptions import ForbiddenException
from app.models.user import RoleEnum
from app.schemas.base import SuccessResponse
from app.schemas.user import User
from app.schemas.prescription import Prescription, PrescriptionCreate, PrescriptionUpdate
from app.schemas.prescription_item import PrescriptionItem, PrescriptionItemCreate, PrescriptionItemUpdate
from app.schemas.drug_interaction import DrugInteractionResponse
from app.services.prescription_service import PrescriptionService

router = APIRouter(prefix="/prescriptions", tags=["Prescriptions"])


def _can_view_rx(current_user: User, rx: Prescription) -> bool:
    if current_user.role == RoleEnum.ADMIN:
        return True
    if current_user.role == RoleEnum.DOCTOR and rx.doctor_id == current_user.id:
        return True
    if rx.patient_id == current_user.id:
        return True
    return False


def _can_edit_rx(current_user: User, rx: Prescription) -> bool:
    if current_user.role == RoleEnum.ADMIN:
        return True
    if current_user.role == RoleEnum.DOCTOR and rx.doctor_id == current_user.id:
        return True
    return False


@router.get("", response_model=SuccessResponse[list[Prescription]])
def list_prescriptions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    svc: PrescriptionService = Depends(get_prescription_service),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[list[Prescription]]:
    # Role’a göre listele
    if current_user.role == RoleEnum.ADMIN:
        rows = svc.prescription_repo.get_all(skip=skip, limit=limit)  # (istersen service method ekleriz)
        data = [Prescription.model_validate(x) for x in rows]
        return SuccessResponse(content=data)

    if current_user.role == RoleEnum.DOCTOR:
        data = svc.get_prescriptions_by_doctor(doctor_id=current_user.id, skip=skip, limit=limit)
        return SuccessResponse(content=data)

    # patient
    data = svc.get_prescriptions_by_patient(patient_id=current_user.id, skip=skip, limit=limit)
    return SuccessResponse(content=data)


@router.get("/active", response_model=SuccessResponse[list[Prescription]])
def list_my_active_prescriptions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    svc: PrescriptionService = Depends(get_prescription_service),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[list[Prescription]]:
    # patient active
    data = svc.get_active_prescriptions(patient_id=current_user.id, skip=skip, limit=limit)
    return SuccessResponse(content=data)


@router.post("", response_model=SuccessResponse[Prescription], status_code=201)
def create_prescription(
    payload: PrescriptionCreate,
    svc: PrescriptionService = Depends(get_prescription_service),
    current_user: User = Depends(get_current_doctor_or_admin),
) -> SuccessResponse[Prescription]:
    # doctor/admin create edebilir; doctor_id = current_user.id
    created = svc.create_prescription(doctor_id=current_user.id, data=payload)
    return SuccessResponse(content=created)


@router.get("/{prescription_id}", response_model=SuccessResponse[Prescription])
def get_prescription(
    prescription_id: uuid.UUID,
    svc: PrescriptionService = Depends(get_prescription_service),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[Prescription]:
    rx = svc.get_prescription_by_id(prescription_id)
    if not _can_view_rx(current_user, rx):
        raise ForbiddenException("You do not have access to this prescription")
    return SuccessResponse(content=rx)


@router.patch("/{prescription_id}", response_model=SuccessResponse[Prescription])
def update_prescription(
    prescription_id: uuid.UUID,
    payload: PrescriptionUpdate,
    svc: PrescriptionService = Depends(get_prescription_service),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[Prescription]:
    rx = svc.get_prescription_by_id(prescription_id)
    if not _can_edit_rx(current_user, rx):
        raise ForbiddenException("You do not have permission to update this prescription")

    updated = svc.update_prescription(prescription_id=prescription_id, data=payload)
    return SuccessResponse(content=updated)


@router.delete("/{prescription_id}", response_model=SuccessResponse[dict])
def delete_prescription(
    prescription_id: uuid.UUID,
    svc: PrescriptionService = Depends(get_prescription_service),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[dict]:
    rx = svc.get_prescription_by_id(prescription_id)
    if not _can_edit_rx(current_user, rx):
        raise ForbiddenException("You do not have permission to delete this prescription")

    svc.delete_prescription(prescription_id)
    return SuccessResponse(content={"deleted": True})


# -------------------------
# Items (nested)
# -------------------------

@router.get("/{prescription_id}/items", response_model=SuccessResponse[list[PrescriptionItem]])
def list_prescription_items(
    prescription_id: uuid.UUID,
    svc: PrescriptionService = Depends(get_prescription_service),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[list[PrescriptionItem]]:
    rx = svc.get_prescription_by_id(prescription_id)
    if not _can_view_rx(current_user, rx):
        raise ForbiddenException("You do not have access to this prescription")

    items = svc.get_all_prescription_items(prescription_id)
    return SuccessResponse(content=items)


@router.post("/{prescription_id}/items", response_model=SuccessResponse[PrescriptionItem], status_code=201)
def add_item(
    prescription_id: uuid.UUID,
    payload: PrescriptionItemCreate,
    svc: PrescriptionService = Depends(get_prescription_service),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[PrescriptionItem]:
    rx = svc.get_prescription_by_id(prescription_id)
    if not _can_edit_rx(current_user, rx):
        raise ForbiddenException("You do not have permission to modify items for this prescription")

    # güvenlik: body’deki prescription_id’yi path ile override et
    payload = payload.model_copy(update={"prescription_id": prescription_id})
    item = svc.add_prescription_item(payload)
    return SuccessResponse(content=item)


@router.post("/{prescription_id}/items/bulk", response_model=SuccessResponse[list[PrescriptionItem]], status_code=201)
def add_items_bulk(
    prescription_id: uuid.UUID,
    payload: list[PrescriptionItemCreate],
    svc: PrescriptionService = Depends(get_prescription_service),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[list[PrescriptionItem]]:
    rx = svc.get_prescription_by_id(prescription_id)
    if not _can_edit_rx(current_user, rx):
        raise ForbiddenException("You do not have permission to modify items for this prescription")

    payload = [p.model_copy(update={"prescription_id": prescription_id}) for p in payload]
    items = svc.add_prescription_items(payload)
    return SuccessResponse(content=items)


# item_id bazlı update/delete için ayrı route daha rahat
@router.patch("/items/{item_id}", response_model=SuccessResponse[PrescriptionItem])
def update_item(
    item_id: uuid.UUID,
    payload: PrescriptionItemUpdate,
    svc: PrescriptionService = Depends(get_prescription_service),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[PrescriptionItem]:
    item = svc.get_prescription_item_by_id(item_id)

    rx = svc.get_prescription_by_id(item.prescription_id)
    if not _can_edit_rx(current_user, rx):
        raise ForbiddenException("You do not have permission to update this item")

    updated = svc.update_prescription_item(item_id=item_id, data=payload)
    return SuccessResponse(content=updated)


@router.delete("/items/{item_id}", response_model=SuccessResponse[dict])
def delete_item(
    item_id: uuid.UUID,
    svc: PrescriptionService = Depends(get_prescription_service),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[dict]:
    item = svc.get_prescription_item_by_id(item_id)
    rx = svc.get_prescription_by_id(item.prescription_id)

    if not _can_edit_rx(current_user, rx):
        raise ForbiddenException("You do not have permission to delete this item")

    svc.delete_prescription_item(item_id)
    return SuccessResponse(content={"deleted": True})


# -------------------------
# Interactions
# -------------------------

@router.get("/{prescription_id}/interactions", response_model=SuccessResponse[list[DrugInteractionResponse]])
def check_prescription_interactions(
    prescription_id: uuid.UUID,
    svc: PrescriptionService = Depends(get_prescription_service),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[list[DrugInteractionResponse]]:
    rx = svc.get_prescription_by_id(prescription_id)
    if not _can_view_rx(current_user, rx):
        raise ForbiddenException("You do not have access to this prescription")

    rows = svc.check_prescription_interactions(prescription_id)
    return SuccessResponse(content=rows)
