from datetime import datetime

from fastapi import APIRouter, Depends, Request
from app.api.deps.auth import get_current_user
from app.api.deps.services import (
    get_appointment_service,
    get_chatbot_service,
    get_prescription_service,
)
from app.core.limiter import limiter
from app.exceptions.exceptions import ForbiddenException
from app.models.appointment import AppointmentStatusEnum
from app.models.prescription import Status as PrescriptionStatus
from app.models.user import RoleEnum
from app.schemas.user import User
from app.schemas.chatbot import ChatRequest, ChatResponse
from app.schemas.prescription import Prescription
from app.services.appointment_service import AppointmentService
from app.services.chatbot_service import ChatbotService
from app.services.prescription_service import PrescriptionService

router = APIRouter()


def _format_prescription(
    prescription_service: PrescriptionService,
    prescription: Prescription,
    current_user: User,
) -> str:
    parts: list[str] = []
    status_value = getattr(getattr(prescription, "status", None), "value", None) or getattr(
        prescription, "status", None
    )
    if status_value:
        parts.append(str(status_value))
    if getattr(prescription, "notes", None):
        parts.append(f"notes: {prescription.notes}")

    meds: list[str] = []
    try:
        items = prescription_service.get_all_prescription_items(prescription.id, current_user)
        for item in items:
            med = prescription_service.med_repo.get_by_id(item.medication_id) if hasattr(
                prescription_service, "med_repo"
            ) else None
            med_name = getattr(med, "commercial_name", None) if med else "Medication"
            med_strength = getattr(med, "strength", None) if med else None
            med_desc = med_name
            if med_strength:
                med_desc += f" {med_strength}"
            if getattr(item, "dosage", None):
                med_desc += f" | dosage: {item.dosage}"
            if getattr(item, "duration", None):
                med_desc += f" | duration: {item.duration} days"
            meds.append(med_desc)
    except Exception:
        # Fail silently for context enrichment; main answer should still work
        meds = []

    if meds:
        parts.append("medications: " + "; ".join(meds))

    return " | ".join(parts)


@router.post("/ask", response_model=ChatResponse, summary="Chat with the assistant")
@limiter.limit("3/minute")
@limiter.limit("100/day")
def ask_chatbot(
    request: Request,
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
    chatbot_service: ChatbotService = Depends(get_chatbot_service),
    appointment_service: AppointmentService = Depends(get_appointment_service),
    prescription_service: PrescriptionService = Depends(get_prescription_service),
):
    """
    Sends a question to the OpenAI-powered chatbot using thread-based sessions.
    """
    if current_user.role != RoleEnum.patient:
        raise ForbiddenException("Only patients can use the chatbot.")

    extra_context = None

    if data.thread_id is None:
        context_parts: list[str] = []
        appointments = appointment_service.get_by_patient(
            patient_id=current_user.id,
            status=AppointmentStatusEnum.booked,
            from_date=datetime.now(),
            limit=5,
        )
        if appointments:
            formatted_appointments = "; ".join(
                " | ".join(
                    part
                    for part in [
                        appt.appointment_datetime.strftime("%Y-%m-%d %H:%M")
                        if getattr(appt, "appointment_datetime", None)
                        else None,
                        getattr(appt, "status", None),
                        getattr(appt, "hospital_name", None),
                        getattr(appt, "clinic_name", None),
                        getattr(appt, "city", None),
                        getattr(appt, "district", None),
                        getattr(appt, "doctor_name", None),
                        f"notes: {appt.notes}" if getattr(appt, "notes", None) else None,
                    ]
                    if part
                )
                for appt in appointments
            )
            context_parts.append(f"Upcoming appointments: {formatted_appointments}")

        prescriptions = prescription_service.patient_list_prescriptions(
            patient_id=current_user.id,
            limit=5,
            status=PrescriptionStatus.active,
        )
        active_prescriptions = [
            p for p in prescriptions if getattr(p, "status", None) == PrescriptionStatus.active
        ]
        if active_prescriptions:
            formatted_prescriptions = "; ".join(
                _format_prescription(prescription_service, p, current_user)
                for p in active_prescriptions
            )
            context_parts.append(f"Active prescriptions: {formatted_prescriptions}")

        if context_parts:
            extra_context = " | ".join(context_parts)
        print(extra_context)
    answer, thread_id = chatbot_service.get_answer(
        question=data.question,
        thread_id=data.thread_id,
        extra_context=extra_context,
        persist_context=data.thread_id is None,
    )
    return ChatResponse(
        answer=answer,
        thread_id=thread_id,
    )
