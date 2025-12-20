import uuid
from fastapi import APIRouter, Depends
from app.api.deps.auth import get_current_user
from app.api.deps.services import get_medication_service
from app.schemas.base import SuccessResponse
from app.schemas.schedule_time import ScheduleTimeResponse
from app.schemas.schedule_time import MarkDoseTakenRequest, MarkDoseSkippedRequest
from app.schemas.user import User
from app.services.medication_service import MedicationService

router = APIRouter(prefix="/schedule-times", tags=["Schedule Times"])

@router.patch("/{schedule_time_id}/take", response_model=SuccessResponse[ScheduleTimeResponse])
def take_dose(
    schedule_time_id: uuid.UUID,
    payload: MarkDoseTakenRequest,
    svc: MedicationService = Depends(get_medication_service),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[ScheduleTimeResponse]:
    row = svc.mark_dose_taken(
        current_user_id=current_user.id,
        schedule_time_id=schedule_time_id,
        taken_at=payload.taken_at,
    )
    return SuccessResponse(content=row)

@router.patch("/{schedule_time_id}/skip", response_model=SuccessResponse[ScheduleTimeResponse])
def skip_dose(
    schedule_time_id: uuid.UUID,
    payload: MarkDoseSkippedRequest,
    svc: MedicationService = Depends(get_medication_service),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[ScheduleTimeResponse]:
    row = svc.mark_dose_skipped(
        current_user_id=current_user.id,
        schedule_time_id=schedule_time_id,
        reason=payload.reason,
    )
    return SuccessResponse(content=row)

@router.patch("/{schedule_time_id}/miss", response_model=SuccessResponse[ScheduleTimeResponse])
def miss_dose(
    schedule_time_id: uuid.UUID,
    svc: MedicationService = Depends(get_medication_service),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[ScheduleTimeResponse]:
    row = svc.mark_dose_missed(
        current_user_id=current_user.id,
        schedule_time_id=schedule_time_id,
    )
    return SuccessResponse(content=row)
