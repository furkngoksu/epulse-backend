from .auth_service import AuthService
from .prescription_service import PrescriptionService
from .appointment_service import AppointmentService
from .doctor_service import DoctorService
from .catalog_service import CatalogService
from .user import UserService

# Doctor patient relationship servisleri domain bazlıya çeviririz sonra burayı düzenleriz kod sadeleşsin diye yapıyom


__all__ = [
    "AuthService",
    "PrescriptionService",
    "AppointmentService",
    "DoctorService",
    "CatalogService",
    "UserService",
]