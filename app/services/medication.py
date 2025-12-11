from datetime import date, datetime, timedelta
import uuid
from app.models.dose_log import DoseLogModel
from app.models.schedule import ScheduleModel
from app.models.schedule_time import ScheduleTimeModel
from app.repositories.medication_repository import MedicationRepository
from app.repositories.patient_medication_repository import PatientMedicationRepository
from app.exceptions.exceptions import NotFoundException
from app.schemas.dose_log import DoseLogCreate, DoseLogResponse, DoseLogUpdate
from app.schemas.medication import MedicationResponse, MedicationCreate, MedicationUpdate
from app.repositories.dose_log_repository import DoseLogRepository
from app.repositories.schedule_repository import ScheduleRepository, ScheduleTimeRepository
from app.models.medication import MedicationModel
from app.schemas.patient_medication import PatientMedicationCreate, PatientMedicationResponse, PatientMedicationUpdate
from app.models.patient_medication import PatientMedicationModel
from app.schemas.schedule import ScheduleCreate, ScheduleResponse, ScheduleUpdate
from app.schemas.schedule_time import ScheduleTimeResponse, ScheduleTimeCreate

class MedicationService:
    def __init__(
        self,
        medication_repo: MedicationRepository,
        patient_medication_repo: PatientMedicationRepository,
        schedule_repo: ScheduleRepository,
        schedule_time_repo: ScheduleTimeRepository,
        dose_log_repo: DoseLogRepository,
    ):
        self.med_repo = medication_repo
        self.pm_repo = patient_medication_repo
        self.schedule_repo = schedule_repo
        self.schedule_time_repo = schedule_time_repo
        self.log_repo = dose_log_repo

    # Medication Methods    

    def get_all_medications(self, skip: int = 0, limit: int = 100) -> list[MedicationResponse]:
        medications = self.med_repo.get_all(skip=skip, limit=limit)
        return [MedicationResponse.model_validate(med) for med in medications]

    def get_medication_by_id(self, medication_id: uuid.UUID) -> MedicationResponse:
        medication = self.med_repo.get_by_id(medication_id)
        if not medication:
            raise NotFoundException(f"Medication not found")
        return MedicationResponse.model_validate(medication)
    
    def search_medications_by_name(self, name: str, skip: int = 0, limit: int = 100) -> list[MedicationResponse]:
        medications = self.med_repo.search_by_name(name=name, skip=skip, limit=limit)
        return [MedicationResponse.model_validate(med) for med in medications]
    
    def create_medication(self, medication_create: MedicationCreate) -> MedicationResponse:
        medication_model = MedicationModel(**medication_create.model_dump())
        medication = self.med_repo.create(medication_model)
        return MedicationResponse.model_validate(medication)
    
    def update_medication(self, medication_id: uuid.UUID, medication_update: MedicationUpdate) -> MedicationResponse:
        medication = self.med_repo.get_by_id(medication_id)
        if not medication:
            raise NotFoundException(f"Medication not found")
        
        for field, value in medication_update.model_dump(exclude_unset=True).items():
            setattr(medication, field, value)
        
        updated_medication = self.med_repo.update(medication)
        return MedicationResponse.model_validate(updated_medication)
    
    def delete_medication(self, medication_id: uuid.UUID) -> None:
        medication = self.med_repo.get_by_id(medication_id)
        if not medication:
            raise NotFoundException(f"Medication not found")
        
        self.med_repo.delete(medication)

    # Patient Medication Methods

    def get_patient_medication_by_patient_id(self, patient_id: uuid.UUID) -> list[PatientMedicationResponse]:
        patient_medications = self.pm_repo.get_by_patient_id(patient_id)
        return [PatientMedicationResponse.model_validate(pm) for pm in patient_medications]

    def get_all_patient_medications(self, skip: int = 0, limit: int = 100) -> list[PatientMedicationResponse]:
        patient_medications = self.pm_repo.get_all(skip=skip, limit=limit)
        return [PatientMedicationResponse.model_validate(pm) for pm in patient_medications]
    
    def get_patient_medication_by_id(self, patient_medication_id: uuid.UUID) -> PatientMedicationResponse:
        patient_medication = self.pm_repo.get_by_id(patient_medication_id)
        if not patient_medication:
            raise NotFoundException(f"Patient Medication not found")
        return PatientMedicationResponse.model_validate(patient_medication)
    
    def get_active_patient_medications(self, user_id: uuid.UUID) -> list[PatientMedicationResponse]:
        patient_medications = self.pm_repo.get_active_by_user_id(user_id)
        return [PatientMedicationResponse.model_validate(pm) for pm in patient_medications]

    def add_patient_medication(self, patient_medication: PatientMedicationCreate) -> PatientMedicationResponse:
        patient_medication_model = PatientMedicationModel(**patient_medication.model_dump())
        created_pm = self.pm_repo.create(patient_medication_model)
        return PatientMedicationResponse.model_validate(created_pm)
    
    def update_patient_medication(self, patient_medication_id: uuid.UUID, patient_medication_update: PatientMedicationUpdate) -> PatientMedicationResponse:
        patient_medication = self.pm_repo.get_by_id(patient_medication_id)
        if not patient_medication:
            raise NotFoundException(f"Patient Medication not found")
        
        for field, value in patient_medication_update.model_dump(exclude_unset=True).items():
            setattr(patient_medication, field, value)
        
        updated_pm = self.pm_repo.update(patient_medication)
        return PatientMedicationResponse.model_validate(updated_pm)
    
    def delete_patient_medication(self, patient_medication_id: uuid.UUID) -> None:
        patient_medication = self.pm_repo.get_by_id(patient_medication_id)
        if not patient_medication:
            raise NotFoundException(f"Patient Medication not found")
        
        self.pm_repo.delete(patient_medication)

    def deactivate_patient_medication(self, patient_medication_id: uuid.UUID) -> PatientMedicationResponse:
        patient_medication = self.pm_repo.get_by_id(patient_medication_id)
        if not patient_medication:
            raise NotFoundException(f"Patient Medication not found")
        
        patient_medication.is_active = False
        updated_pm = self.pm_repo.update(patient_medication)
        return PatientMedicationResponse.model_validate(updated_pm)
    
    def activate_patient_medication(self, patient_medication_id: uuid.UUID) -> PatientMedicationResponse:
        patient_medication = self.pm_repo.get_by_id(patient_medication_id)
        if not patient_medication:
            raise NotFoundException(f"Patient Medication not found")
        
        patient_medication.is_active = True
        updated_pm = self.pm_repo.update(patient_medication)
        return PatientMedicationResponse.model_validate(updated_pm)
    
    # Schedule Methods

    def get_medication_schedules(self, patient_medication_id: uuid.UUID):
        pm = self.pm_repo.get_by_id(patient_medication_id)
        if not pm:
            raise NotFoundException(f"Patient Medication not found")
        schedules = pm.schedules
        return [ScheduleResponse.model_validate(sch) for sch in schedules]

    def get_medication_schedule_by_id(self, schedule_id: uuid.UUID):
        schedule = self.schedule_repo.get_by_id(schedule_id)
        if not schedule:
            raise NotFoundException(f"Schedule not found")
        return ScheduleResponse.model_validate(schedule)

    def create_medication_schedule(self, schedule_data: ScheduleCreate) -> ScheduleResponse:
        pm = self.pm_repo.get_by_id(schedule_data.patient_medication_id)
        if not pm:
            raise NotFoundException(f"Patient Medication not found")

        schedule_model = ScheduleModel(**schedule_data.model_dump())
        schedule = self.schedule_repo.create_schedule(schedule_model)
        return ScheduleResponse.model_validate(schedule)

    def delete_medication_schedule(self, schedule_id: uuid.UUID) -> None:
        schedule = self.schedule_repo.get_by_id(schedule_id)
        if not schedule:
            raise NotFoundException(f"Schedule not found")
        
        self.schedule_repo.delete_schedule(schedule_id)

    def update_medication_schedule(self, schedule_data: ScheduleUpdate) -> ScheduleResponse:
        schedule = self.schedule_repo.get_by_id(schedule_data.id)
        if not schedule:
            raise NotFoundException(f"Schedule not found")
        
        for field, value in schedule_data.model_dump(exclude_unset=True).items():
            setattr(schedule, field, value)

        updated_schedule = self.schedule_repo.update_schedule(schedule=schedule)
        return ScheduleResponse.model_validate(updated_schedule)
    
    # Schedule Time Methods

    def get_schedule_times(self, schedule_id: uuid.UUID) -> list[ScheduleTimeResponse]:
        schedule = self.schedule_repo.get_by_id(schedule_id)
        if not schedule:
            raise NotFoundException(f"Schedule not found")
        schedule_times = schedule.schedule_times
        return [ScheduleTimeResponse.model_validate(st) for st in schedule_times]
    
    def get_schedule_time_by_id(self, schedule_time_id: uuid.UUID) -> ScheduleTimeResponse:
        schedule_time = self.schedule_time_repo.get_by_id(schedule_time_id)
        if not schedule_time:
            raise NotFoundException(f"Schedule Time not found")
        return ScheduleTimeResponse.model_validate(schedule_time)
    
    def add_schedule_time(self, schedule_time_data: ScheduleTimeCreate) -> ScheduleTimeResponse:
        schedule = self.schedule_repo.get_by_id(schedule_time_data.schedule_id)
        if not schedule:
            raise NotFoundException(f"Schedule not found")

        schedule_time_model = ScheduleTimeModel(**schedule_time_data.model_dump())
        schedule_time = self.schedule_time_repo.create_schedule_time(schedule_time_model)
        return ScheduleTimeResponse.model_validate(schedule_time)
    
    def delete_schedule_time(self, schedule_time_id: uuid.UUID) -> None:
        schedule_time = self.schedule_time_repo.get_by_id(schedule_time_id)
        if not schedule_time:
            raise NotFoundException(f"Schedule Time not found")
        
        self.schedule_time_repo.delete_schedule_time(schedule_time_id)

    # Dose Logs Methods

    def get_dose_log_by_id(self, dose_log_id: uuid.UUID) -> DoseLogResponse:
        dose_log = self.log_repo.get_by_id(dose_log_id)
        if not dose_log:
            raise NotFoundException(f"Dose Log not found")
        return DoseLogResponse.model_validate(dose_log)

    def get_dose_logs(self, skip: int = 0, limit: int = 100) -> list[DoseLogResponse]:
        dose_logs = self.log_repo.get_all(skip=skip, limit=limit)
        return [DoseLogResponse.model_validate(dl) for dl in dose_logs]
    
    def create_dose_log(self, dose_log: DoseLogCreate) -> DoseLogResponse:
        dose_log_model = DoseLogModel(**dose_log.model_dump())
        created_log = self.log_repo.create(dose_log_model)
        return DoseLogResponse.model_validate(created_log)

    def update_dose_log(self, dose_log_id: uuid.UUID, dose_log_update: DoseLogUpdate) -> DoseLogResponse:
        dose_log = self.log_repo.get_by_id(dose_log_id)
        if not dose_log:
            raise NotFoundException(f"Dose Log not found")

        for field, value in dose_log_update.model_dump(exclude_unset=True).items():
            setattr(dose_log, field, value)

        updated_log = self.log_repo.update(dose_log)
        return DoseLogResponse.model_validate(updated_log)
    
    def delete_dose_log(self, dose_log_id: uuid.UUID) -> None:
        dose_log = self.log_repo.get_by_id(dose_log_id)
        if not dose_log:
            raise NotFoundException(f"Dose Log not found")
        
        self.log_repo.delete(dose_log)

    # Additional Methods

    def get_medications_between(self, patient_id: uuid.UUID, range_start: date, range_end: date):
        patient_medications = self.pm_repo.get_medications_for_date_range(patient_id, range_start, range_end)
        return [PatientMedicationResponse.model_validate(pm) for pm in patient_medications]
    
    # def get_upcoming_medications(self, patient_id: uuid.UUID, hours: int) -> list[PatientMedicationResponse]:
        now = datetime.now()
        end = now + timedelta(hours=hours)
        today = now.date()
        meds = self.pm_repo.get_upcoming_medications(
            patient_id=patient_id,
            today=today,
            now=now,
            end=end,
        )
        return [PatientMedicationResponse.model_validate(m) for m in meds]

    # def get_compliance_rate_for_patient(self, patient_id: uuid.UUID, range_start: date, range_end: date) -> float:

        if range_start > range_end:
            raise ValueError("range_start must be before range_end")
        
        if self.get_patient_medication_by_id(patient_id) is None:
            raise NotFoundException(f"Patient not found")

        patient_medications = self.pm_repo.get_medications_for_date_range(patient_id, range_start, range_end)
        
        total_doses = 0
        taken_doses = 0

        for pm in patient_medications:
            for schedule in pm.schedules:
                # Calculate number of doses scheduled in the date range
                schedule_start = max(schedule.start_date, range_start)
                schedule_end = min(schedule.end_date, range_end)
                days_active = (schedule_end - schedule_start).days + 1
                
                doses_per_day = len(schedule.schedule_times)
                total_doses += days_active * doses_per_day

                # Count taken doses from dose logs
                for log in pm.dose_logs:
                    if schedule_start <= log.scheduled_time <= schedule_end and log.taken_time:
                        taken_doses += 1

        if total_doses == 0:
            return 0.0
        
        compliance_rate = (taken_doses / total_doses) * 100
        return compliance_rate
    
    # def get_compliance_rate_for_medication(self, patient_medication_id: uuid.UUID, range_start: date, range_end: date) -> float:
        pm = self.pm_repo.get_by_id(patient_medication_id)
        if not pm:
            raise NotFoundException(f"Patient Medication not found")
        
        total_doses = 0
        taken_doses = 0

        for schedule in pm.schedules:
            # Calculate number of doses scheduled in the date range
            schedule_start = max(schedule.start_date, range_start)
            schedule_end = min(schedule.end_date, range_end)
            days_active = (schedule_end - schedule_start).days + 1

            doses_per_day = len(schedule.schedule_times)
            total_doses += days_active * doses_per_day

            # Count taken doses from dose logs
            for log in pm.dose_logs:
                if schedule_start <= log.scheduled_time <= schedule_end and log.taken_time:
                    taken_doses += 1

        if total_doses == 0:
            return 0.0

        compliance_rate = (taken_doses / total_doses) * 100
        return compliance_rate

        pass

    # def get_missed_doses(self, patient_id: uuid.UUID, start: datetime, end: datetime) -> list[DoseLogResponse]:
        missed_dose_logs = self.log_repo.get_missed_doses(patient_id, start, end)
        return [DoseLogResponse.model_validate(dl) for dl in missed_dose_logs]

    def send_medication_reminders(self):
        # This is a placeholder for sending medication reminders.
        # The actual implementation would depend on the notification system in place.
        pass
        
