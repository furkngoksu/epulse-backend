import uuid
from datetime import datetime

from sqlalchemy import asc
from sqlalchemy.orm import Session, selectinload

from app.models.schedule_time import ScheduleTimeModel, DoseStatusEnum
from app.models.schedule import ScheduleModel
from app.models.patient_medication import PatientMedicationModel


class ScheduleRepository:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_by_id(self, schedule_id: uuid.UUID) -> ScheduleModel | None:
        return (
            self.db.query(ScheduleModel).filter(ScheduleModel.id == schedule_id).first()
        )

    def create(self, schedule: ScheduleModel) -> ScheduleModel:
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        return schedule

    def update(self, schedule: ScheduleModel) -> ScheduleModel:
        self.db.commit()
        self.db.refresh(schedule)
        return schedule

    def delete(self, schedule: ScheduleModel) -> None:
        self.db.delete(schedule)
        self.db.commit()


class ScheduleTimeRepository:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_by_id(self, schedule_time_id: uuid.UUID) -> ScheduleTimeModel | None:
        return (
            self.db.query(ScheduleTimeModel)
            .filter(ScheduleTimeModel.id == schedule_time_id)
            .first()
        )

    def create(self, schedule_time: ScheduleTimeModel) -> ScheduleTimeModel:
        self.db.add(schedule_time)
        self.db.commit()
        self.db.refresh(schedule_time)
        return schedule_time

    def create_many(
        self, schedule_times: list[ScheduleTimeModel]
    ) -> list[ScheduleTimeModel]:
        if not schedule_times:
            return []
        self.db.add_all(schedule_times)
        self.db.commit()
        for st in schedule_times:
            self.db.refresh(st)
        return schedule_times

    def update(self, schedule_time: ScheduleTimeModel) -> ScheduleTimeModel:
        self.db.commit()
        self.db.refresh(schedule_time)
        return schedule_time

    def delete(self, schedule_time: ScheduleTimeModel) -> None:
        self.db.delete(schedule_time)
        self.db.commit()

    def list_for_patient_between(
        self,
        patient_id: uuid.UUID,
        start: datetime,
        end: datetime,
        status: DoseStatusEnum | None = None,
    ) -> list[ScheduleTimeModel]:
        q = (
            self.db.query(ScheduleTimeModel)
            .join(ScheduleModel, ScheduleTimeModel.schedule_id == ScheduleModel.id)
            .join(
                PatientMedicationModel,
                ScheduleModel.patient_medication_id == PatientMedicationModel.id,
            )
            .options(
                selectinload(ScheduleTimeModel.schedule)
                .selectinload(ScheduleModel.patient_medication)
                .selectinload(PatientMedicationModel.medication)
            )
            .filter(PatientMedicationModel.user_id == patient_id)
            .filter(PatientMedicationModel.is_active.is_(True))
            .filter(ScheduleTimeModel.dose_datetime.between(start, end))
        )

        if status is not None:
            q = q.filter(ScheduleTimeModel.status == status)

        return q.order_by(asc(ScheduleTimeModel.dose_datetime)).all()

    def get_next_pending_dose(
        self,
        patient_id: uuid.UUID,
        now: datetime,
    ) -> ScheduleTimeModel | None:
        return (
            self.db.query(ScheduleTimeModel)
            .join(ScheduleModel, ScheduleTimeModel.schedule_id == ScheduleModel.id)
            .join(
                PatientMedicationModel,
                ScheduleModel.patient_medication_id == PatientMedicationModel.id,
            )
            .options(
                selectinload(ScheduleTimeModel.schedule)
                .selectinload(ScheduleModel.patient_medication)
                .selectinload(PatientMedicationModel.medication)
            )
            .filter(PatientMedicationModel.user_id == patient_id)
            .filter(PatientMedicationModel.is_active.is_(True))
            .filter(ScheduleTimeModel.status == DoseStatusEnum.pending)
            .filter(ScheduleTimeModel.dose_datetime >= now)
            .order_by(asc(ScheduleTimeModel.dose_datetime))
            .first()
        )

    def mark_taken(
        self,
        schedule_time: ScheduleTimeModel,
        taken_at: datetime | None = None,
    ) -> ScheduleTimeModel:
        schedule_time.status = DoseStatusEnum.taken
        schedule_time.taken_at = taken_at or datetime.now(
            tz=schedule_time.dose_datetime.tzinfo
        )
        schedule_time.skip_reason = None
        return self.update(schedule_time)

    def mark_missed(self, schedule_time: ScheduleTimeModel) -> ScheduleTimeModel:
        schedule_time.status = DoseStatusEnum.missed
        schedule_time.taken_at = None
        schedule_time.skip_reason = None
        return self.update(schedule_time)

    def mark_skipped(
        self,
        schedule_time: ScheduleTimeModel,
        skip_reason: str | None = None,
    ) -> ScheduleTimeModel:
        schedule_time.status = DoseStatusEnum.skipped
        schedule_time.taken_at = None
        schedule_time.skip_reason = skip_reason
        return self.update(schedule_time)

    def reset_to_pending(self, schedule_time: ScheduleTimeModel) -> ScheduleTimeModel:
        schedule_time.status = DoseStatusEnum.pending
        schedule_time.taken_at = None
        schedule_time.skip_reason = None
        return self.update(schedule_time)

    def bulk_mark_missed_for_past(
        self,
        patient_id: uuid.UUID,
        now: datetime,
    ) -> int:
        rows = (
            self.db.query(ScheduleTimeModel)
            .join(ScheduleModel, ScheduleTimeModel.schedule_id == ScheduleModel.id)
            .join(
                PatientMedicationModel,
                ScheduleModel.patient_medication_id == PatientMedicationModel.id,
            )
            .filter(PatientMedicationModel.user_id == patient_id)
            .filter(PatientMedicationModel.is_active.is_(True))
            .filter(ScheduleTimeModel.status == DoseStatusEnum.pending)
            .filter(ScheduleTimeModel.dose_datetime < now)
            .all()
        )

        for st in rows:
            st.status = DoseStatusEnum.missed
            st.taken_at = None
            st.skip_reason = None

        self.db.commit()
        return len(rows)

    def get_by_id_with_patient_medication(
        self, schedule_time_id: uuid.UUID
    ) -> ScheduleTimeModel | None:
        return (
            self.db.query(ScheduleTimeModel)
            .options(
                selectinload(ScheduleTimeModel.schedule).selectinload(
                    ScheduleModel.patient_medication
                )
            )
            .filter(ScheduleTimeModel.id == schedule_time_id)
            .first()
        )
