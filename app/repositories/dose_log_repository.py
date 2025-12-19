from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from app.models.dose_log import DoseLogModel, DoseStatusEnum
from app.models.patient_medication import PatientMedicationModel

class DoseLogRepository:

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_all(self, skip: int = 0, limit: int = 100) -> list[DoseLogModel]:
        return self.db_session.query(DoseLogModel).offset(skip).limit(limit).all()

    def get_by_id(self, dose_log_id: uuid.UUID) -> DoseLogModel | None:
        return self.db_session.query(DoseLogModel).filter(DoseLogModel.id == dose_log_id).first()

    def get_by_patient_id(self, patient_id: uuid.UUID) -> list[DoseLogModel]:
        return (
            self.db_session.query(DoseLogModel)
            .join(
                PatientMedicationModel,
                DoseLogModel.patient_medication_id == PatientMedicationModel.id
            )
            .filter(PatientMedicationModel.user_id == patient_id)
            .all()
        )

    def create(self, dose_log: DoseLogModel) -> DoseLogModel:
        self.db_session.add(dose_log)
        self.db_session.commit()
        self.db_session.refresh(dose_log)
        return dose_log

    def update(self, dose_log: DoseLogModel) -> DoseLogModel:
        self.db_session.commit()
        self.db_session.refresh(dose_log)
        return dose_log

    def delete(self, dose_log: DoseLogModel) -> None:
        self.db_session.delete(dose_log)
        self.db_session.commit()

    def get_missed_doses(self, patient_id: uuid.UUID, start: datetime, end: datetime) -> list[DoseLogModel]:
        return (
            self.db_session.query(DoseLogModel)
            .join(
                PatientMedicationModel,
                DoseLogModel.patient_medication_id == PatientMedicationModel.id
            )
            .filter(PatientMedicationModel.user_id == patient_id)
            .filter(DoseLogModel.status == DoseStatusEnum.missed)
            .filter(DoseLogModel.scheduled_time.between(start, end))
            .all()
        )