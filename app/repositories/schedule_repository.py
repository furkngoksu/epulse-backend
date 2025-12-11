from app.models.patient_medication import PatientMedicationModel
from app.models.schedule import ScheduleModel
from sqlalchemy.orm import Session
import uuid

from app.models.schedule_time import ScheduleTimeModel

class ScheduleRepository:
    def __init__(self, db_session: Session):
        self.db = db_session

    def create_schedule(self, schedule: ScheduleModel) -> ScheduleModel:
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        return schedule

    def get_by_id(self, schedule_id: uuid.UUID) -> ScheduleModel | None:
        return self.db.query(ScheduleModel).filter(ScheduleModel.id == schedule_id).first()

    def update_schedule(self, schedule: ScheduleModel) -> ScheduleModel:
        self.db.commit()
        self.db.refresh(schedule)
        return schedule

    def delete_schedule(self, schedule_id: uuid.UUID) -> bool:
        self.db.query(ScheduleModel).filter(ScheduleModel.id == schedule_id).delete()
        self.db.commit()
        if self.get_by_id(schedule_id) is None:
            return True
        return False
    
    def get_all_schedule_for_patient_today(self, patient_id: uuid.UUID, date) -> list[ScheduleModel]:
        return (
            self.db.query(ScheduleModel)
            .join(PatientMedicationModel, ScheduleModel.patient_medication_id == PatientMedicationModel.id)
            .join(ScheduleTimeModel, ScheduleModel.id == ScheduleTimeModel.schedule_id)
            .filter(PatientMedicationModel.is_active == True)
            .filter(PatientMedicationModel.user_id == patient_id)
            .filter(ScheduleModel.start_date <= date)
            .filter(ScheduleModel.end_date >= date)
            .all()
        )

class ScheduleTimeRepository:
    def __init__(self, db_session: Session):
        self.db = db_session

    def create_schedule_time(self, schedule_time: ScheduleTimeModel) -> ScheduleTimeModel:
        self.db.add(schedule_time)
        self.db.commit()
        self.db.refresh(schedule_time)
        return schedule_time

    def get_by_id(self, schedule_time_id: uuid.UUID) -> ScheduleTimeModel | None:
        return self.db.query(ScheduleTimeModel).filter(ScheduleTimeModel.id == schedule_time_id).first()

    def update_schedule_time(self, schedule_time: ScheduleTimeModel) -> ScheduleTimeModel:
        self.db.commit()
        self.db.refresh(schedule_time)
        return schedule_time

    def delete_schedule_time(self, schedule_time_id: uuid.UUID) -> bool:
        self.db.query(ScheduleTimeModel).filter(ScheduleTimeModel.id == schedule_time_id).delete()
        self.db.commit()
        if self.get_by_id(schedule_time_id) is None:
            return True
        return False
