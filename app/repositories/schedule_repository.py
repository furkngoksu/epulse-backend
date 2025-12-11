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

    def get_schedule(self, schedule_id: uuid.UUID) -> ScheduleModel | None:
        return self.db.query(ScheduleModel).filter(ScheduleModel.id == schedule_id).first()

    def update_schedule(self, schedule_id: uuid.UUID, schedule: ScheduleModel) -> ScheduleModel:
        self.db.query(ScheduleModel).filter(ScheduleModel.id == schedule_id).update(schedule)
        self.db.commit()
        return schedule

    def delete_schedule(self, schedule_id: uuid.UUID) -> bool:
        self.db.query(ScheduleModel).filter(ScheduleModel.id == schedule_id).delete()
        self.db.commit()
        if self.get_schedule(schedule_id) is None:
            return True
        return False


class ScheduleTimeRepository:
    def __init__(self, db_session: Session):
        self.db = db_session

    def create_schedule_time(self, schedule_time: ScheduleTimeModel) -> ScheduleTimeModel:
        self.db.add(schedule_time)
        self.db.commit()
        self.db.refresh(schedule_time)
        return schedule_time

    def get_schedule_time(self, schedule_time_id: uuid.UUID) -> ScheduleTimeModel | None:
        return self.db.query(ScheduleTimeModel).filter(ScheduleTimeModel.id == schedule_time_id).first()

    def update_schedule_time(self, schedule_time_id: uuid.UUID, schedule_time: ScheduleTimeModel) -> ScheduleTimeModel:
        self.db.query(ScheduleTimeModel).filter(ScheduleTimeModel.id == schedule_time_id).update(schedule_time)
        self.db.commit()
        return schedule_time

    def delete_schedule_time(self, schedule_time_id: uuid.UUID) -> bool:
        self.db.query(ScheduleTimeModel).filter(ScheduleTimeModel.id == schedule_time_id).delete()
        self.db.commit()
        if self.get_schedule_time(schedule_time_id) is None:
            return True
        return False
