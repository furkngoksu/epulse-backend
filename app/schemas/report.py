from uuid import UUID
from pydantic import BaseModel, Field


class AdherenceRateResponse(BaseModel):
    adherence_rate: float = Field(..., description="Adherence rate percentage (0-100)")
    total_doses: int = Field(
        ..., description="Total number of doses (taken + missed + skipped)"
    )
    taken_doses: int = Field(..., description="Number of taken doses")
    missed_doses: int = Field(..., description="Number of missed doses")
    skipped_doses: int = Field(..., description="Number of skipped doses")
    pending_doses: int = Field(..., description="Number of pending doses")


class DoseCountResponse(BaseModel):
    count: int = Field(..., description="Number of doses with the specified status")
    status: str = Field(..., description="Status filter applied")


class MedicationAdherenceResponse(BaseModel):
    patient_medication_id: UUID
    medication_id: UUID
    custom_name: str
    commercial_name: str
    adherence_rate: float = Field(
        ..., description="Adherence rate for this medication (0-100)"
    )
    total_doses: int
    taken_doses: int
    missed_doses: int
    skipped_doses: int
    current_stock: int
    tablets_per_use: int


class BasicStatsResponse(BaseModel):
    patient_id: UUID
    first_name: str
    last_name: str
    age: int
    active_medications_count: int
    overall_adherence_rate: float = Field(
        ..., description="Overall adherence rate (0-100)"
    )
    pending_doses_today: int


class UserCountResponse(BaseModel):
    total_users: int = Field(..., description="Total number of users in the system")
    total_admins: int = Field(..., description="Total number of admin users")
    total_doctors: int = Field(..., description="Total number of doctor users")
    total_patients: int = Field(..., description="Total number of patient users")
