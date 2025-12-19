from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.user import router as user_router
from app.api.v1.hospital import router as hospital_router
from app.api.v1.doctor_profile import router as doctor_profile_router
from app.api.v1.medication import router as medication_router
from app.api.v1.catalog import router as catalog_router
from app.api.v1.drug_interaction import router as drug_interaction_router
from app.api.v1.doctor_patient_relationship import router as doctor_patient_relationship_router
from app.api.v1.appointment import router as appointment_router

app_router = APIRouter(prefix="/api/v1")

app_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app_router.include_router(user_router, prefix="/user", tags=["User"])
app_router.include_router(hospital_router, prefix="/hospitals", tags=["Hospitals"])
app_router.include_router(doctor_profile_router, prefix="/doctor-profiles", tags=["Doctor Profiles"])
app_router.include_router(medication_router, prefix="/medications", tags=["Medications"])
app_router.include_router(catalog_router, prefix="/catalog", tags=["Catalog"])
app_router.include_router(drug_interaction_router, prefix="/drug-interactions", tags=["Drug Interactions"])
app_router.include_router(doctor_patient_relationship_router, prefix="/doctor-patient-relationships", tags=["Doctor-Patient Relationships"])
app_router.include_router(appointment_router, prefix="/appointments", tags=["Appointments"])