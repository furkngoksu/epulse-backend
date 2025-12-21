from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps.auth import get_current_user
from app.api.deps.services import get_report_service
from app.models.schedule_time import DoseStatusEnum
from app.schemas.base import SuccessResponse
from app.schemas.report import (
    AdherenceRateResponse,
    BasicStatsResponse,
    DoseCountResponse,
    MedicationAdherenceResponse,
)
from app.schemas.user import User
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/{patient_id}/adherence-rate", response_model=SuccessResponse[AdherenceRateResponse])
def get_adherence_rate(
    patient_id: UUID,
    start_date: date = Query(..., description="Start date for the report"),
    end_date: date = Query(..., description="End date for the report"),
    current_user: User = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service),
) -> SuccessResponse[AdherenceRateResponse]:
    """
    Get adherence rate for a patient within a date range.

    Adherence rate = (taken doses / (taken + missed + skipped)) * 100
    """
    result = report_service.get_adherence_rate(
        patient_id=patient_id,
        start_date=start_date,
        end_date=end_date,
    )
    return SuccessResponse(content=result)


@router.get("/{patient_id}/dose-count", response_model=SuccessResponse[DoseCountResponse])
def get_dose_count(
    patient_id: UUID,
    start_date: date = Query(..., description="Start date for the report"),
    end_date: date = Query(..., description="End date for the report"),
    status: DoseStatusEnum = Query(..., description="Dose status to count (pending, taken, missed, skipped)"),
    current_user: User = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service),
) -> SuccessResponse[DoseCountResponse]:
    """
    Get the number of doses with a specific status for a patient within a date range.
    """
    result = report_service.get_number_of_doses(
        patient_id=patient_id,
        start_date=start_date,
        end_date=end_date,
        status=status,
    )
    return SuccessResponse(content=result)


@router.get("/{patient_id}/active-medications", response_model=SuccessResponse[list[MedicationAdherenceResponse]])
def get_active_medications(
    patient_id: UUID,
    current_user: User = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service),
) -> SuccessResponse[list[MedicationAdherenceResponse]]:
    """
    Get all active medications for a patient with adherence rate for each medication.
    """
    result = report_service.get_active_medications(patient_id=patient_id)
    return SuccessResponse(content=result)


@router.get("/{patient_id}/basic-stats", response_model=SuccessResponse[BasicStatsResponse])
def get_basic_stats(
    patient_id: UUID,
    current_user: User = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service),
) -> SuccessResponse[BasicStatsResponse]:
    """
    Get basic statistics for a patient:
    - Patient info (id, name, age)
    - Number of active medications
    - Overall adherence rate
    - Number of pending doses for today
    """
    result = report_service.get_basic_stats(patient_id=patient_id)
    return SuccessResponse(content=result)
