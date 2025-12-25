import uuid
import logging
from datetime import date, datetime, timezone
from functools import wraps

from sqlalchemy.orm import Session, selectinload

from app.exceptions import NotFoundException
from app.models.patient_medication import PatientMedicationModel
from app.models.schedule import ScheduleModel
from app.models.schedule_time import ScheduleTimeModel, DoseStatusEnum
from app.repositories.patient_medication_repository import PatientMedicationRepository
from app.repositories.schedule_repository import ScheduleTimeRepository
from app.repositories.user_repository import UserRepository
from app.schemas.report import (
    AdherenceRateResponse,
    DoseCountResponse,
    MedicationAdherenceResponse,
    BasicStatsResponse,
)
from app.services.medication_service import MedicationService

logger = logging.getLogger(__name__)


class ReportService:
    def __init__(
        self,
        user_repo: UserRepository,
        patient_medication_repo: PatientMedicationRepository,
        schedule_time_repo: ScheduleTimeRepository,
        db_session: Session,
        medication_service: MedicationService,
    ):
        self.user_repo = user_repo
        self.pm_repo = patient_medication_repo
        self.st_repo = schedule_time_repo
        self.db = db_session
        self.medication_service = medication_service

    @staticmethod
    def _mark_missed_doses(
        medication_service: MedicationService,
        patient_id: uuid.UUID,
        pm_repo: PatientMedicationRepository,
        st_repo: ScheduleTimeRepository,
    ):
        medication_service.mark_dose_missed(
            current_user_id=patient_id,
            pm_repo=pm_repo,
            st_repo=st_repo,
        )

    def get_adherence_rate(
        self,
        patient_id: uuid.UUID,
        start_date: date,
        end_date: date,
    ) -> AdherenceRateResponse:
        self._mark_missed_doses(self.medication_service, patient_id, self.pm_repo, self.st_repo)
        """
        Calculate adherence rate for a patient within a date range.
        Adherence rate = (taken doses / (taken + missed + skipped)) * 100
        """
        # Convert dates to datetime with timezone
        start_datetime = datetime.combine(start_date, datetime.min.time()).replace(
            tzinfo=timezone.utc
        )
        end_datetime = datetime.combine(end_date, datetime.max.time()).replace(
            tzinfo=timezone.utc
        )

        # Query all doses for the patient in the date range
        doses = self.st_repo.list_for_patient_between(
            patient_id=patient_id,
            start=start_datetime,
            end=end_datetime,
        )

        # Count doses by status
        taken = sum(1 for d in doses if d.status == DoseStatusEnum.taken)
        missed = sum(1 for d in doses if d.status == DoseStatusEnum.missed)
        skipped = sum(1 for d in doses if d.status == DoseStatusEnum.skipped)
        pending = sum(1 for d in doses if d.status == DoseStatusEnum.pending)

        # Calculate adherence rate
        total_completed = taken + missed + skipped
        adherence_rate = (taken / total_completed * 100) if total_completed > 0 else 0.0

        return AdherenceRateResponse(
            adherence_rate=round(adherence_rate, 2),
            total_doses=total_completed,
            taken_doses=taken,
            missed_doses=missed,
            skipped_doses=skipped,
            pending_doses=pending,
        )

    def get_number_of_doses(
        self,
        patient_id: uuid.UUID,
        start_date: date,
        end_date: date,
        status: DoseStatusEnum,
    ) -> DoseCountResponse:
        self._mark_missed_doses(self.medication_service, patient_id, self.pm_repo, self.st_repo)
        """
        Get the number of doses with a specific status for a patient within a date range.
        """
        # Convert dates to datetime with timezone
        start_datetime = datetime.combine(start_date, datetime.min.time()).replace(
            tzinfo=timezone.utc
        )
        end_datetime = datetime.combine(end_date, datetime.max.time()).replace(
            tzinfo=timezone.utc
        )

        # Query doses with the specified status
        doses = self.st_repo.list_for_patient_between(
            patient_id=patient_id,
            start=start_datetime,
            end=end_datetime,
            status=status,
        )

        return DoseCountResponse(
            count=len(doses),
            status=status.value,
        )

    def get_active_medications(
        self,
        patient_id: uuid.UUID,
    ) -> list[MedicationAdherenceResponse]:
        self._mark_missed_doses(self.medication_service, patient_id, self.pm_repo, self.st_repo)
        """
        Get all active medications for a patient with adherence rate for each.
        """
        # Get all active patient medications
        active_meds = self.pm_repo.get_active_by_user_id(user_id=patient_id)

        if not active_meds:
            return []

        results = []

        for pm in active_meds:
            # Get all schedule times for this patient medication
            # Join through schedules to get all schedule times
            doses = (
                self.db.query(ScheduleTimeModel)
                .join(ScheduleModel, ScheduleTimeModel.schedule_id == ScheduleModel.id)
                .filter(ScheduleModel.patient_medication_id == pm.id)
                .all()
            )

            # Count doses by status
            taken = sum(1 for d in doses if d.status == DoseStatusEnum.taken)
            missed = sum(1 for d in doses if d.status == DoseStatusEnum.missed)
            skipped = sum(1 for d in doses if d.status == DoseStatusEnum.skipped)

            # Calculate adherence rate
            total_completed = taken + missed + skipped
            adherence_rate = (
                (taken / total_completed * 100) if total_completed > 0 else 0.0
            )

            # Load medication details if not already loaded
            if not pm.medication:
                pm = (
                    self.db.query(PatientMedicationModel)
                    .options(selectinload(PatientMedicationModel.medication))
                    .filter(PatientMedicationModel.id == pm.id)
                    .first()
                )

            if pm:
                results.append(
                    MedicationAdherenceResponse(
                        patient_medication_id=pm.id,
                        medication_id=pm.medication_id,
                        custom_name=pm.custom_name,
                        commercial_name=pm.medication.commercial_name
                        if pm.medication
                        else "",
                        adherence_rate=round(adherence_rate, 2),
                        total_doses=total_completed,
                        taken_doses=taken,
                        missed_doses=missed,
                        skipped_doses=skipped,
                        current_stock=pm.current_stock,
                        tablets_per_use=pm.tablets_per_use,
                    )
                )

        return results

    def get_basic_stats(
        self,
        patient_id: uuid.UUID,
    ) -> BasicStatsResponse:
        self._mark_missed_doses(self.medication_service, patient_id, self.pm_repo, self.st_repo)
        """
        Get basic statistics for a patient:
        - Patient info (id, name, age)
        - Number of active medications
        - Overall adherence rate
        - Number of pending doses for today
        """
        # Get user/patient
        user = self.user_repo.get_by_id(patient_id)
        if not user:
            raise NotFoundException("Patient not found")

        # Calculate age
        today = date.today()
        age = (
            today.year
            - user.date_of_birth.year
            - (
                (today.month, today.day)
                < (user.date_of_birth.month, user.date_of_birth.day)
            )
        )

        # Get number of active medications
        active_meds = self.pm_repo.get_active_by_user_id(user_id=patient_id)
        active_medications_count = len(active_meds)

        # Calculate overall adherence rate (all time)
        all_doses = (
            self.db.query(ScheduleTimeModel)
            .join(ScheduleModel, ScheduleTimeModel.schedule_id == ScheduleModel.id)
            .join(
                PatientMedicationModel,
                ScheduleModel.patient_medication_id == PatientMedicationModel.id,
            )
            .filter(PatientMedicationModel.user_id == patient_id)
            .filter(PatientMedicationModel.is_active)
            .all()
        )

        taken = sum(1 for d in all_doses if d.status == DoseStatusEnum.taken)
        missed = sum(1 for d in all_doses if d.status == DoseStatusEnum.missed)
        skipped = sum(1 for d in all_doses if d.status == DoseStatusEnum.skipped)

        total_completed = taken + missed + skipped
        overall_adherence_rate = (
            (taken / total_completed * 100) if total_completed > 0 else 0.0
        )

        # Get pending doses for today
        today_start = datetime.combine(today, datetime.min.time()).replace(
            tzinfo=timezone.utc
        )
        today_end = datetime.combine(today, datetime.max.time()).replace(
            tzinfo=timezone.utc
        )

        pending_today = self.st_repo.list_for_patient_between(
            patient_id=patient_id,
            start=today_start,
            end=today_end,
            status=DoseStatusEnum.pending,
        )

        return BasicStatsResponse(
            patient_id=patient_id,
            first_name=user.first_name,
            last_name=user.last_name,
            age=age,
            active_medications_count=active_medications_count,
            overall_adherence_rate=round(overall_adherence_rate, 2),
            pending_doses_today=len(pending_today),
        )
