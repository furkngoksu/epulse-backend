import uuid
from datetime import datetime, timedelta, timezone, date, time
import math
from zoneinfo import ZoneInfo

from app.exceptions.exceptions import NotFoundException, BadRequestException
from app.models.medication import MedicationModel
from app.models.patient_medication import PatientMedicationModel
from app.models.schedule import ScheduleModel
from app.models.schedule_time import ScheduleTimeModel, DoseStatusEnum
from app.repositories.medication_repository import MedicationRepository
from app.repositories.patient_medication_repository import PatientMedicationRepository
from app.repositories.schedule_repository import ScheduleRepository, ScheduleTimeRepository
from app.repositories.medication_alias_repository import MedicationAliasRepository
from app.schemas.medication import MedicationCreate, MedicationUpdate, MedicationResponse
from app.schemas.patient_medication import (
    PatientMedicationUpdate,
    PatientMedicationResponse,
    PatientMedicationWithScheduleCreate,
)
from app.schemas.schedule import ScheduleCreate, ScheduleResponse
from app.schemas.schedule_time import ScheduleTimeCreate, ScheduleTimeResponse
from app.schemas.medication_alias import MedicationAliasResponse
from app.models.medication_alias import MedicationAliasModel

class MedicationService:
    def __init__(
        self,
        medication_repo: MedicationRepository,
        patient_medication_repo: PatientMedicationRepository,
        schedule_repo: ScheduleRepository,
        schedule_time_repo: ScheduleTimeRepository,
        medication_alias_repo: MedicationAliasRepository,
    ):
        self.med_repo = medication_repo
        self.pm_repo = patient_medication_repo
        self.schedule_repo = schedule_repo
        self.st_repo = schedule_time_repo
        self.alias_repo = medication_alias_repo

    # -------- #
    # Catalog
    # -------- #

    def list_catalog(self, skip: int = 0, limit: int = 100) -> list[MedicationResponse]:
        meds = self.med_repo.get_all(skip=skip, limit=limit)
        return [MedicationResponse.model_validate(m) for m in meds]

    def get_catalog_medication(self, medication_id: uuid.UUID) -> MedicationResponse:
        med = self.med_repo.get_by_id(medication_id)
        if not med:
            raise NotFoundException("Medication not found")
        return MedicationResponse.model_validate(med)

    def create_catalog_medication(self, data: MedicationCreate) -> MedicationResponse:
        model = MedicationModel(**data.model_dump())
        med = self.med_repo.create(model)
        return MedicationResponse.model_validate(med)

    def update_catalog_medication(self, medication_id: uuid.UUID, data: MedicationUpdate) -> MedicationResponse:
        med = self.med_repo.get_by_id(medication_id)
        if not med:
            raise NotFoundException("Medication not found")

        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(med, k, v)

        med = self.med_repo.update(med)
        return MedicationResponse.model_validate(med)

    def delete_catalog_medication(self, medication_id: uuid.UUID) -> None:
        med = self.med_repo.get_by_id(medication_id)
        if not med:
            raise NotFoundException("Medication not found")
        self.med_repo.delete(med)

    # -------- #
    # Patient Medications
    # -------- #

    def list_patient_medications(
        self,
        user_id: uuid.UUID,
        status: str = "all",
        skip: int = 0,
        limit: int = 100,
    ) -> list[PatientMedicationResponse]:

        if status == "active":
            is_active = True
        elif status == "paused":
            is_active = False
        elif status == "all":
            is_active = None
        else:
            raise BadRequestException("Invalid status. Use active|paused|all")

        rows = self.pm_repo.list_by_user(
            user_id=user_id,
            is_active=is_active,
            skip=skip,
            limit=limit,
        )
        return [PatientMedicationResponse.model_validate(pm) for pm in rows]

    def get_patient_medication(
        self,
        patient_medication_id: uuid.UUID,
        current_user_id: uuid.UUID,
    ) -> PatientMedicationResponse:
        pm = self.pm_repo.get_by_id_for_user(
            patient_medication_id=patient_medication_id,
            user_id=current_user_id,
        )
        if not pm:
            raise NotFoundException("Patient medication not found")
        return PatientMedicationResponse.model_validate(pm)

    def update_patient_medication(
        self,
        patient_medication_id: uuid.UUID,
        data: PatientMedicationUpdate,
        current_user_id: uuid.UUID,
    ) -> PatientMedicationResponse:
        pm = self.pm_repo.get_by_id_for_user(
            patient_medication_id=patient_medication_id,
            user_id=current_user_id,
        )
        if not pm:
            raise NotFoundException("Patient medication not found")

        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(pm, k, v)

        pm = self.pm_repo.update(pm)
        return PatientMedicationResponse.model_validate(pm)


    def delete_patient_medication(
        self,
        patient_medication_id: uuid.UUID,
        current_user_id: uuid.UUID,
    ) -> None:
        pm = self.pm_repo.get_by_id_for_user(
            patient_medication_id=patient_medication_id,
            user_id=current_user_id,
        )
        if not pm:
            raise NotFoundException("Patient medication not found")

        self.pm_repo.delete(pm)

    
    def get_upcoming_patient_medications(self, patient_id: uuid.UUID, hours: int) -> list[PatientMedicationResponse]:
        now = datetime.now(timezone.utc)
        end = now + timedelta(hours=hours)
        meds = self.pm_repo.get_upcoming_medications(patient_id=patient_id, now=now, end=end)
        return [PatientMedicationResponse.model_validate(m) for m in meds]

    def get_patient_medications_between(
        self, patient_id: uuid.UUID, range_start: date, range_end: date
    ) -> list[PatientMedicationResponse]:
        rows = self.pm_repo.get_medications_for_date_range(patient_id, range_start, range_end)
        return [PatientMedicationResponse.model_validate(pm) for pm in rows]
    
    def _iter_dates(self, start: date, end: date):
        d = start
        while d <= end:
            yield d
            d += timedelta(days=1)
    
    def create_patient_medication_with_schedule(
        self,
        patient_id: uuid.UUID,
        data: PatientMedicationWithScheduleCreate,
    ) -> PatientMedicationResponse:
        med = self.med_repo.get_by_id(data.medication_id)
        if not med:
            raise NotFoundException("Medication not found")

        if data.initial_stock < data.tablets_per_use:
            raise BadRequestException("initial_stock must be >= tablets_per_use")

        times = data.schedule.times
        if not times:
            raise BadRequestException("schedule.times cannot be empty")

        if any(dt.tzinfo is None for dt in times):
            raise BadRequestException("All schedule times must be timezone-aware")

        times_utc = sorted({dt.astimezone(timezone.utc) for dt in times})
        if not times_utc:
            raise BadRequestException("Schedule times cannot be empty")

        start_date: date = times_utc[0].date()
        end_date: date = times_utc[-1].date()

        stock_warning_threshold = max(1, math.ceil(data.initial_stock * 0.10))

        schedule_times = [
            ScheduleTimeModel(
                dose_datetime=dt,  # UTC
                status=DoseStatusEnum.pending,
            )
            for dt in times_utc
        ]

        custom_name = data.custom_name or getattr(med, "commercial_name", None) or "Medication"

        schedule = ScheduleModel(
            start_date=start_date,
            end_date=end_date,
            schedule_times=schedule_times,  # cascade
        )

        pm = PatientMedicationModel(
            user_id=patient_id,
            medication_id=data.medication_id,
            custom_name=custom_name,
            initial_stock=data.initial_stock,
            current_stock=data.initial_stock,
            stock_warning_threshold=stock_warning_threshold,
            is_active=True,
            tablets_per_use=data.tablets_per_use,
            schedules=[schedule],  # cascade
        )

        created = self.pm_repo.create(pm)
        return PatientMedicationResponse.model_validate(created)


    # -------- #
    # Schedules and Schedule Times
    # -------- #

    def create_schedule(self, data: ScheduleCreate) -> ScheduleResponse:
        pm = self.pm_repo.get_by_id(data.patient_medication_id)
        if not pm:
            raise NotFoundException("Patient medication not found")

        schedule = ScheduleModel(**data.model_dump())
        schedule = self.schedule_repo.create(schedule)
        return ScheduleResponse.model_validate(schedule)

    def add_schedule_time(self, schedule_id: uuid.UUID, data: ScheduleTimeCreate) -> ScheduleTimeResponse:
        schedule = self.schedule_repo.get_by_id(schedule_id)
        if not schedule:
            raise NotFoundException("Schedule not found")

        st = ScheduleTimeModel(
            schedule_id=schedule_id,
            dose_datetime=data.dose_datetime,
            status=DoseStatusEnum.pending,
        )
        st = self.st_repo.create(st)
        return ScheduleTimeResponse.model_validate(st)

    def mark_dose_taken(self, schedule_time_id: uuid.UUID, current_user_id: uuid.UUID, taken_at: datetime | None = None) -> ScheduleTimeResponse:
        st = self.st_repo.get_by_id_with_patient_medication(schedule_time_id)
        if not st:
            raise NotFoundException("Schedule time not found")
        
        pm = st.schedule.patient_medication
        if pm.user_id != current_user_id:
            raise BadRequestException("User does not own this schedule time")

        if st.status == DoseStatusEnum.taken:
            return ScheduleTimeResponse.model_validate(st)

        if st.status != DoseStatusEnum.pending:
            raise BadRequestException("Only PENDING doses can be marked as TAKEN")

        pm = st.schedule.patient_medication
        need = pm.tablets_per_use or 1

        if pm.current_stock < need:
            raise BadRequestException("Not enough stock")

        pm.current_stock -= need

        st.status = DoseStatusEnum.taken
        st.taken_at = taken_at or datetime.now(timezone.utc)
        st.skip_reason = None

        st = self.st_repo.update(st)
        return ScheduleTimeResponse.model_validate(st)

    def mark_dose_skipped(self, schedule_time_id: uuid.UUID, current_user_id: uuid.UUID, reason: str | None = None) -> ScheduleTimeResponse:
        st = self.st_repo.get_by_id(schedule_time_id)
        if not st:
            raise NotFoundException("Schedule time not found")

        pm = st.schedule.patient_medication
        if pm.user_id != current_user_id:
            raise BadRequestException("User does not own this schedule time")

        st.status = DoseStatusEnum.skipped
        st.taken_at = None
        st.skip_reason = reason

        st = self.st_repo.update(st)
        return ScheduleTimeResponse.model_validate(st)

    def mark_dose_missed(self, schedule_time_id: uuid.UUID, current_user_id: uuid.UUID) -> ScheduleTimeResponse:
        st = self.st_repo.get_by_id(schedule_time_id)
        if not st:
            raise NotFoundException("Schedule time not found")

        pm = st.schedule.patient_medication
        if pm.user_id != current_user_id:
            raise BadRequestException("User does not own this schedule time")

        st.status = DoseStatusEnum.missed
        st.taken_at = None
        st.skip_reason = None

        st = self.st_repo.update(st)
        return ScheduleTimeResponse.model_validate(st)

    # -------- #
    # Medication Aliases
    # -------- #

    def set_alias(
        self, user_id: uuid.UUID, medication_id: uuid.UUID, alias_name: str
    ) -> MedicationAliasResponse:
        # Validate medication exists
        med = self.med_repo.get_by_id(medication_id)
        if not med:
            raise NotFoundException("Medication not found")

        # Check if alias already exists for this user+medication
        existing = self.alias_repo.get_by_user_and_medication(user_id, medication_id)

        if existing:
            # Update existing alias
            existing.alias_name = alias_name
            alias = self.alias_repo.update(existing)
        else:
            # Create new alias
            alias = MedicationAliasModel(
                user_id=user_id,
                medication_id=medication_id,
                alias_name=alias_name,
            )
            alias = self.alias_repo.create(alias)

        return MedicationAliasResponse.model_validate(alias)

    def get_aliases(self, user_id: uuid.UUID) -> list[MedicationAliasResponse]:
        aliases = self.alias_repo.get_all_by_user(user_id)
        return [MedicationAliasResponse.model_validate(a) for a in aliases]

    def delete_alias(self, alias_id: uuid.UUID, user_id: uuid.UUID) -> None:
        alias = self.alias_repo.get_by_id_for_user(alias_id, user_id)
        if not alias:
            raise NotFoundException("Medication alias not found")
        self.alias_repo.delete(alias)
