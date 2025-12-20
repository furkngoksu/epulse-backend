import uuid
from datetime import datetime, timedelta, timezone, date
import math

from app.exceptions.exceptions import NotFoundException, BadRequestException
from app.models.medication import MedicationModel
from app.models.patient_medication import PatientMedicationModel
from app.models.schedule import ScheduleModel
from app.models.schedule_time import ScheduleTimeModel, DoseStatusEnum
from app.repositories.medication_repository import MedicationRepository
from app.repositories.patient_medication_repository import PatientMedicationRepository
from app.repositories.schedule_repository import ScheduleRepository, ScheduleTimeRepository
from app.schemas.medication import MedicationCreate, MedicationUpdate, MedicationResponse
from app.schemas.patient_medication import (
    PatientMedicationCreate,
    PatientMedicationCreatedResponse,
    PatientMedicationUpdate,
    PatientMedicationResponse,
    PatientMedicationWithScheduleCreate,
)
from app.schemas.schedule import ScheduleCreate, ScheduleResponse
from app.schemas.schedule_time import ScheduleTimeCreate, ScheduleTimeResponse
from app.schemas.user import User


class MedicationService:
    def __init__(
        self,
        medication_repo: MedicationRepository,
        patient_medication_repo: PatientMedicationRepository,
        schedule_repo: ScheduleRepository,
        schedule_time_repo: ScheduleTimeRepository,
    ):
        self.med_repo = medication_repo
        self.pm_repo = patient_medication_repo
        self.schedule_repo = schedule_repo
        self.st_repo = schedule_time_repo

    def list_catalog(self, skip: int = 0, limit: int = 100) -> list[MedicationResponse]:
        meds = self.med_repo.get_all(skip=skip, limit=limit)
        return [MedicationResponse.model_validate(m) for m in meds]

    def get_catalog_medication(self, medication_id: uuid.UUID) -> MedicationResponse:
        med = self.med_repo.get_by_id(medication_id)
        if not med:
            raise NotFoundException("Medication not found")
        return MedicationResponse.model_validate(med)

    def search_catalog(self, name: str, skip: int = 0, limit: int = 100) -> list[MedicationResponse]:
        meds = self.med_repo.search_by_name(name=name, skip=skip, limit=limit)
        return [MedicationResponse.model_validate(m) for m in meds]

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


    def list_patient_medications(
        self,
        user_id: uuid.UUID,
        status: str = "all",
        skip: int = 0,
        limit: int = 100,
    ) -> list[PatientMedicationResponse]:
        
        if status == "active":
            rows = self.pm_repo.get_active_by_user_id(user_id)
        elif status == "paused":
            # paused = is_active False
            rows = self.pm_repo.get_by_patient_id(user_id)
            rows = [r for r in rows if not r.is_active]
        elif status == "all":
            rows = self.pm_repo.get_by_patient_id(user_id)
        else:
            raise BadRequestException("Invalid status. Use active|paused|all")

        rows = rows[skip : skip + limit]
        return [PatientMedicationResponse.model_validate(pm) for pm in rows]

    def get_patient_medication(self, patient_medication_id: uuid.UUID) -> PatientMedicationResponse:
        pm = self.pm_repo.get_by_id(patient_medication_id)
        if not pm:
            raise NotFoundException("Patient medication not found")
        return PatientMedicationResponse.model_validate(pm)

    def create_patient_medication(self, data: PatientMedicationCreate) -> PatientMedicationResponse:
        pm = PatientMedicationModel(**data.model_dump())
        created = self.pm_repo.create(pm)
        return PatientMedicationResponse.model_validate(created)

    def update_patient_medication(
        self,
        patient_medication_id: uuid.UUID,
        data: PatientMedicationUpdate,
    ) -> PatientMedicationResponse:
        pm = self.pm_repo.get_by_id(patient_medication_id)
        if not pm:
            raise NotFoundException("Patient medication not found")

        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(pm, k, v)

        pm = self.pm_repo.update(pm)
        return PatientMedicationResponse.model_validate(pm)

    def delete_patient_medication(self, patient_medication_id: uuid.UUID) -> None:
        pm = self.pm_repo.get_by_id(patient_medication_id)
        if not pm:
            raise NotFoundException("Patient medication not found")
        self.pm_repo.delete(pm)

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
            status=DoseStatusEnum.PENDING,
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

        if st.status == DoseStatusEnum.TAKEN:
            return ScheduleTimeResponse.model_validate(st)

        if st.status != DoseStatusEnum.PENDING:
            raise BadRequestException("Only PENDING doses can be marked as TAKEN")

        pm = st.schedule.patient_medication
        need = pm.tablets_per_use or 1

        if pm.current_stock < need:
            raise BadRequestException("Not enough stock")

        pm.current_stock -= need

        st.status = DoseStatusEnum.TAKEN
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

        st.status = DoseStatusEnum.SKIPPED
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

        st.status = DoseStatusEnum.MISSED
        st.taken_at = None
        st.skip_reason = None

        st = self.st_repo.update(st)
        return ScheduleTimeResponse.model_validate(st)

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
    
    def create_patient_medication_with_schedule(
        self,
        current_user_id: uuid.UUID,
        data: PatientMedicationWithScheduleCreate,
    ) -> PatientMedicationCreatedResponse:
        med = self.med_repo.get_by_id(data.medication_id)
        if not med:
            raise NotFoundException("Medication not found")

        initial_stock = data.initial_stock
        if initial_stock < data.tablets_per_use:
            raise BadRequestException("initial_stock must be >= tablets_per_use")


        stock_warning_threshold = max(1, math.ceil(initial_stock * 0.10))

        for dt in data.schedule.times:
            if not (data.start_date <= dt <= data.end_date):
                raise BadRequestException("All schedule times must be between start_date and end_date")

        custom_name = data.custom_name or med.commercial_name

        schedule_times = [
            ScheduleTimeModel(
                dose_datetime=dt,
                status=DoseStatusEnum.PENDING,
            )
            for dt in data.schedule.times
        ]

        schedule = ScheduleModel(
            start_date=data.start_date,
            end_date=data.end_date,
            frequency_type=data.frequency_type,
            specific_days=data.specific_days,
            schedule_times=schedule_times,  # cascade
        )

        pm = PatientMedicationModel(
            user_id=current_user_id,
            medication_id=data.medication_id,
            custom_name=custom_name,
            initial_stock=initial_stock,
            current_stock=initial_stock,
            stock_warning_threshold=stock_warning_threshold,
            is_active=True,
            tablets_per_use=data.tablets_per_use,
            schedules=[schedule],  # cascade
        )

        created = self.pm_repo.create(pm)  # TEK commit burada
        return PatientMedicationCreatedResponse(patient_medication_id=created.id)
