from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.user import router as user_router
from app.api.v1.hospital import router as hospital_router
from app.api.v1.clinic import router as clinic_router
from app.api.v1.doctor_profile import router as doctor_profile_router
from app.api.v1.patient_medications import router as medication_router
from app.api.v1.catalog import router as catalog_router
from app.api.v1.doctor_patient_relationship import router as doctor_patient_relationship_router
from app.api.v1.appointment import router as appointment_router
from app.api.v1.prescription import router as prescription_router
from app.api.v1.schedule_times import router as schedule_time_router
from app.api.v1.test import router as test_router
from app.api.v1.reports import router as reports_router

app_router = APIRouter(prefix="/api/v1")

app_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app_router.include_router(user_router)
app_router.include_router(hospital_router, prefix="/hospitals", tags=["Hospitals"])
app_router.include_router(clinic_router, prefix="/clinics", tags=["Clinics"])
app_router.include_router(doctor_profile_router, prefix="/doctor-profiles", tags=["Doctor Profiles"])
app_router.include_router(catalog_router)
app_router.include_router(doctor_patient_relationship_router, prefix="/doctor-patient-relationships", tags=["Doctor-Patient Relationships"])
app_router.include_router(appointment_router, prefix="/appointments", tags=["Appointments"])
app_router.include_router(prescription_router)
app_router.include_router(schedule_time_router)
app_router.include_router(medication_router)
app_router.include_router(test_router, tags=["Test"])
app_router.include_router(reports_router)