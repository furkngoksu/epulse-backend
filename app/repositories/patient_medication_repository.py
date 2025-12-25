from typing import Optional
from app.models.patient_medication import PatientMedicationModel
import uuid
from sqlalchemy.orm import Session

from app.models.schedule import ScheduleModel
from app.models.schedule_time import ScheduleTimeModel
from sqlalchemy.orm import selectinload
from datetime import date, datetime


class PatientMedicationRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_all(self, skip: int = 0, limit: int = 100) -> list[PatientMedicationModel]:
        return (
            self.db_session.query(PatientMedicationModel)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_patient_id(self, patient_id: uuid.UUID) -> list[PatientMedicationModel]:
        return (
            self.db_session.query(PatientMedicationModel)
            .filter_by(user_id=patient_id)
            .all()
        )

    def get_by_id(
        self, patient_medication_id: uuid.UUID
    ) -> PatientMedicationModel | None:
        return (
            self.db_session.query(PatientMedicationModel)
            .filter_by(id=patient_medication_id)
            .first()
        )

    def create(
        self, patient_medication: PatientMedicationModel
    ) -> PatientMedicationModel:
        self.db_session.add(patient_medication)
        self.db_session.commit()
        self.db_session.refresh(patient_medication)
        return patient_medication

    def update(
        self, patient_medication: PatientMedicationModel
    ) -> PatientMedicationModel:
        obj = self.db_session.merge(patient_medication)
        self.db_session.commit()
        self.db_session.refresh(obj)
        return obj

    def delete(self, patient_medication: PatientMedicationModel) -> None:
        self.db_session.delete(patient_medication)
        self.db_session.commit()

    def get_active_by_user_id(self, user_id: uuid.UUID) -> list[PatientMedicationModel]:
        return (
            self.db_session.query(PatientMedicationModel)
            .filter_by(user_id=user_id, is_active=True)
            .all()
        )

    def get_medications_for_date_range(
        self, patient_id: uuid.UUID, range_start: date, range_end: date
    ):
        return (
            self.db_session.query(PatientMedicationModel)
            .options(
                selectinload(PatientMedicationModel.medication),
                selectinload(PatientMedicationModel.schedules).selectinload(
                    ScheduleModel.schedule_times
                ),
            )
            .join(
                ScheduleModel,
                PatientMedicationModel.id == ScheduleModel.patient_medication_id,
            )
            .filter(PatientMedicationModel.user_id == patient_id)
            .filter(PatientMedicationModel.is_active)
            .filter(ScheduleModel.start_date <= range_end)
            .filter(ScheduleModel.end_date >= range_start)
            .all()
        )

    def get_upcoming_medications(
        self,
        patient_id: uuid.UUID,
        now: datetime,
        end: datetime,
    ) -> list[PatientMedicationModel]:
        return (
            self.db_session.query(PatientMedicationModel)
            .distinct(PatientMedicationModel.id)
            .options(
                selectinload(PatientMedicationModel.medication),
                selectinload(PatientMedicationModel.schedules).selectinload(
                    ScheduleModel.schedule_times
                ),
            )
            .join(
                ScheduleModel,
                PatientMedicationModel.id == ScheduleModel.patient_medication_id,
            )
            .join(ScheduleTimeModel, ScheduleModel.id == ScheduleTimeModel.schedule_id)
            .filter(PatientMedicationModel.user_id == patient_id)
            .filter(PatientMedicationModel.is_active)
            .filter(ScheduleTimeModel.dose_datetime.between(now, end))
            .all()
        )

    def list_by_user(
        self,
        user_id: uuid.UUID,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[PatientMedicationModel]:
        q = self.db_session.query(PatientMedicationModel).filter(
            PatientMedicationModel.user_id == user_id
        )

        if is_active is not None:
            q = q.filter(PatientMedicationModel.is_active.is_(is_active))

        return q.offset(skip).limit(limit).all()

    def get_by_id_for_user(
        self,
        patient_medication_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> PatientMedicationModel | None:
        return (
            self.db_session.query(PatientMedicationModel)
            .filter(PatientMedicationModel.id == patient_medication_id)
            .filter(PatientMedicationModel.user_id == user_id)
            .first()
        )
