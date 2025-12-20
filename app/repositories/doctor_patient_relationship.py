import uuid
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, case
from app.models.doctor_patient_relationship import DoctorPatientRelationship
from app.models.user import UserModel
from app.models.patient_medication import PatientMedicationModel
from app.models.schedule import ScheduleModel
from app.models.schedule_time import ScheduleTimeModel, DoseStatusEnum


class DoctorPatientRelationshipRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> list[DoctorPatientRelationship]:
        return self.db.query(DoctorPatientRelationship).offset(skip).limit(limit).all()

    def get_by_id(self, relationship_id: uuid.UUID) -> DoctorPatientRelationship | None:
        return self.db.query(DoctorPatientRelationship).filter(
            DoctorPatientRelationship.id == relationship_id
        ).first()

    def get_by_doctor_and_patient(
        self, doctor_id: uuid.UUID, patient_id: uuid.UUID
    ) -> DoctorPatientRelationship | None:
        """Check if a relationship already exists between a doctor and patient."""
        return self.db.query(DoctorPatientRelationship).filter(
            and_(
                DoctorPatientRelationship.doctor_id == doctor_id,
                DoctorPatientRelationship.patient_id == patient_id
            )
        ).first()

    def get_patients_for_doctor(self, doctor_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[DoctorPatientRelationship]:
        """Get all patients for a specific doctor."""
        return self.db.query(DoctorPatientRelationship).filter(
            DoctorPatientRelationship.doctor_id == doctor_id
        ).offset(skip).limit(limit).all()

    def get_patient_summaries_for_doctor(self, doctor_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[dict]:
        """Get patient summaries with basic info for a specific doctor."""
        results = self.db.query(
            UserModel.id.label("patient_id"),
            UserModel.first_name,
            UserModel.last_name,
            UserModel.date_of_birth
        ).join(
            DoctorPatientRelationship,
            DoctorPatientRelationship.patient_id == UserModel.id
        ).filter(
            DoctorPatientRelationship.doctor_id == doctor_id
        ).offset(skip).limit(limit).all()

        # Calculate age and additional metrics for each patient
        today = date.today()
        patient_summaries = []

        for patient in results:
            # Calculate age
            age = today.year - patient.date_of_birth.year
            if today.month < patient.date_of_birth.month or \
               (today.month == patient.date_of_birth.month and today.day < patient.date_of_birth.day):
                age -= 1

            # Count active prescriptions
            active_prescriptions = self.db.query(func.count(PatientMedicationModel.id)).filter(
                and_(
                    PatientMedicationModel.user_id == patient.patient_id,
                    PatientMedicationModel.is_active == True
                )
            ).scalar() or 0

            # Calculate adherence rate
            dose_counts = self.db.query(
                func.count(case((ScheduleTimeModel.status == DoseStatusEnum.taken, 1))).label("taken"),
                func.count(case((ScheduleTimeModel.status == DoseStatusEnum.missed, 1))).label("missed"),
                func.count(case((ScheduleTimeModel.status == DoseStatusEnum.skipped, 1))).label("skipped")
            ).join(
                ScheduleModel,
                ScheduleTimeModel.schedule_id == ScheduleModel.id
            ).join(
                PatientMedicationModel,
                ScheduleModel.patient_medication_id == PatientMedicationModel.id
            ).filter(
                PatientMedicationModel.user_id == patient.patient_id
            ).first()

            taken = dose_counts.taken or 0
            missed = dose_counts.missed or 0
            skipped = dose_counts.skipped or 0

            total_relevant_doses = taken + missed + skipped
            adherence_rate = (taken / total_relevant_doses * 100) if total_relevant_doses > 0 else 0.0

            patient_summaries.append({
                "patient_id": patient.patient_id,
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "age": age,
                "active_prescriptions": active_prescriptions,
                "adherence_rate": round(adherence_rate, 2)
            })

        return patient_summaries

    def get_doctors_for_patient(self, patient_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[DoctorPatientRelationship]:
        """Get all doctors for a specific patient."""
        return self.db.query(DoctorPatientRelationship).filter(
            DoctorPatientRelationship.patient_id == patient_id
        ).offset(skip).limit(limit).all()

    def create(self, relationship: DoctorPatientRelationship) -> DoctorPatientRelationship:
        self.db.add(relationship)
        self.db.commit()
        self.db.refresh(relationship)
        return relationship

    def delete(self, relationship: DoctorPatientRelationship) -> None:
        self.db.delete(relationship)
        self.db.commit()
