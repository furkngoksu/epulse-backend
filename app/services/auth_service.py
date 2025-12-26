import uuid
import logging
import secrets
from datetime import datetime, timedelta
from app.repositories import UserRepository
from app.repositories.password_reset_request_repository import (
    PasswordResetRequestRepository,
)
from app.repositories.doctor_profile_repository import DoctorProfileRepository
from app.repositories.clinic_repository import ClinicRepository
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    RegisterResponse,
    LoginResponse,
    RegisterDoctorRequest,
    RegisterDoctorResponse,
)
from app.schemas.password_reset import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    VerifyOTPRequest,
    VerifyOTPResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
)
from app.core.security import (
    decode_token,
    hash_password,
    create_access_token,
    create_refresh_token,
    verify_password,
)
from app.exceptions import (
    ConflictException,
    NotFoundException,
    UnauthorizedException,
    BadRequestException,
)
from app.schemas.auth import UserResponse
from app.schemas.doctor_profile import DoctorProfileResponse
from app.models.user import UserModel, RoleEnum
from app.models.doctor_profile import DoctorProfile
from app.models.password_reset_request import PasswordResetRequestModel
from app.services.email_service import email_service

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        reset_request_repository: PasswordResetRequestRepository,
        doctor_profile_repository: DoctorProfileRepository,
        clinic_repository: ClinicRepository,
    ):
        self.user_repository = user_repository
        self.reset_request_repository = reset_request_repository
        self.doctor_profile_repository = doctor_profile_repository
        self.clinic_repository = clinic_repository

    def register(self, request: RegisterRequest) -> RegisterResponse:
        existing_email = self.user_repository.get_by_email(email=request.email)
        if existing_email:
            logger.warning(
                "Register failed: Email already exists", extra={"email": request.email}
            )
            raise ConflictException("Email already exists")

        existing_tc = self.user_repository.get_by_national_id(
            national_id=request.national_id
        )
        if existing_tc:
            logger.warning(
                "Register failed: National ID already exists",
                extra={"national_id": request.national_id},
            )
            raise ConflictException("National ID already registered")

        password_hash = hash_password(request.password)
        user = UserModel(
            national_id=request.national_id,
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            phone_number=request.phone_number,
            password_hash=password_hash,
            date_of_birth=request.date_of_birth,
            gender=request.gender,
        )
        saved_user = self.user_repository.create(user=user)
        access_token = create_access_token({"sub": str(saved_user.id)})
        refresh_token = create_refresh_token({"sub": str(saved_user.id)})

        logger.info(
            "User registered successfully",
            extra={"user_id": str(saved_user.id), "role": saved_user.role.value},
        )

        return RegisterResponse(
            user=UserResponse.model_validate(saved_user),
            access_token=access_token,
            refresh_token=refresh_token,
        )

    def login(self, request: LoginRequest) -> LoginResponse:
        user = self.user_repository.get_by_national_id(national_id=request.national_id)
        if not user:
            logger.warning(
                "Login failed: User not found",
                extra={"national_id": request.national_id},
            )
            raise UnauthorizedException("Invalid national ID or password")

        if not verify_password(request.password, user.password_hash):
            logger.warning(
                "Login failed: incorrect password", extra={"user_id": str(user.id)}
            )
            raise UnauthorizedException("Invalid national ID or password")

        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        logger.info("Login successfull", extra={"user_id": str(user.id)})

        return LoginResponse(
            success=True,
            user=UserResponse.model_validate(user),
            access_token=access_token,
            refresh_token=refresh_token,
        )

    def refresh_token(self, request: RefreshTokenRequest) -> LoginResponse:
        payload = decode_token(request.refresh_token, refresh=True)
        user_id = payload.get("sub")

        user = self.user_repository.get_by_id(uuid.UUID(user_id))
        if not user:
            raise UnauthorizedException("User not found")

        new_access_token = create_access_token({"sub": user_id})
        new_refresh_token = create_refresh_token({"sub": user_id})

        return LoginResponse(
            success=True,
            user=UserResponse.model_validate(user),
            access_token=new_access_token,
            refresh_token=new_refresh_token,
        )

    # ==================== Password Reset Flow ====================

    def forgot_password(self, request: ForgotPasswordRequest) -> ForgotPasswordResponse:
        user = self.user_repository.get_by_email(request.email)

        if not user:
            logger.warning(
                "Forgot password: Email not found", extra={"email": request.email}
            )
            raise NotFoundException("Email not found")

        existing_request = self.reset_request_repository.get_active_by_user(user.id)
        if existing_request and existing_request.resend_count >= 5:
            logger.warning(
                "Forgot password: Resend limit reached", extra={"user_id": str(user.id)}
            )
            raise BadRequestException(
                "Too many reset requests. Please try again later."
            )

        otp_code = "".join([str(secrets.randbelow(10)) for _ in range(6)])
        otp_hash = hash_password(otp_code)

        expires_at = datetime.utcnow() + timedelta(minutes=10)
        reset_request = PasswordResetRequestModel(
            user_id=user.id,
            otp_hash=otp_hash,
            expires_at=expires_at,
        )

        created_request = self.reset_request_repository.create(reset_request)

        email_sent = email_service.send_otp_email(user.email, otp_code)

        if email_sent:
            logger.info(
                "Password reset OTP sent successfully",
                extra={"request_id": str(created_request.id), "user_id": str(user.id)},
            )
        else:
            logger.warning(
                "Failed to send password reset OTP",
                extra={"request_id": str(created_request.id), "user_id": str(user.id)},
            )

        return ForgotPasswordResponse(request_id=created_request.id)

    def verify_otp(self, request: VerifyOTPRequest) -> VerifyOTPResponse:
        reset_request = self.reset_request_repository.get_by_id(request.request_id)
        if not reset_request:
            raise NotFoundException("Invalid request ID")

        if reset_request.used_at:
            raise BadRequestException("This reset request has already been used")

        if reset_request.expires_at < datetime.utcnow():
            raise BadRequestException("OTP has expired")

        if reset_request.locked_at:
            raise BadRequestException("Too many failed attempts. Request a new OTP.")

        if reset_request.attempt_count >= 5:
            reset_request.locked_at = datetime.utcnow()
            self.reset_request_repository.update(reset_request)
            logger.warning(
                "OTP locked: Too many failed attempts",
                extra={"request_id": str(request.request_id)},
            )
            raise BadRequestException("Too many failed attempts. Request a new OTP.")

        if not verify_password(request.otp, reset_request.otp_hash):
            self.reset_request_repository.increment_attempt(reset_request)
            logger.warning(
                "OTP verification failed: Invalid code",
                extra={
                    "request_id": str(request.request_id),
                    "attempts": reset_request.attempt_count + 1,
                },
            )
            raise UnauthorizedException("Invalid OTP code")

        reset_token = secrets.token_urlsafe(32)
        reset_token_hash = hash_password(reset_token)

        reset_request.reset_token_hash = reset_token_hash
        reset_request.verified_at = datetime.utcnow()
        self.reset_request_repository.update(reset_request)

        logger.info(
            "OTP verified successfully",
            extra={
                "request_id": str(request.request_id),
                "user_id": str(reset_request.user_id),
            },
        )

        return VerifyOTPResponse(reset_token=reset_token)

    def reset_password(self, request: ResetPasswordRequest) -> ResetPasswordResponse:
        all_requests = self.reset_request_repository.get_verified_unused_requests()

        # Find matching token
        matching_request = None
        for req in all_requests:
            if req.reset_token_hash and verify_password(
                request.reset_token, req.reset_token_hash
            ):
                matching_request = req
                break

        if not matching_request:
            logger.warning("Password reset failed: Invalid or expired token")
            raise UnauthorizedException("Invalid or expired reset token")

        # Update password
        user = self.user_repository.get_by_id(matching_request.user_id)
        if not user:
            raise NotFoundException("User not found")

        user.password_hash = hash_password(request.new_password)
        self.user_repository.update(user)

        # Mark request as used
        self.reset_request_repository.mark_as_used(matching_request)

        # Send confirmation email
        email_service.send_password_changed_notification(user.email)

        return ResetPasswordResponse()

    # ==================== Doctor Registration ====================

    def register_doctor(self, request: RegisterDoctorRequest) -> RegisterDoctorResponse:
        # Validation phase
        existing_email = self.user_repository.get_by_email(email=request.email)
        if existing_email:
            logger.warning(
                "Register doctor failed: Email already exists",
                extra={"email": request.email},
            )
            raise ConflictException("Email already exists")

        existing_tc = self.user_repository.get_by_national_id(
            national_id=request.national_id
        )
        if existing_tc:
            logger.warning(
                "Register doctor failed: National ID already exists",
                extra={"national_id": request.national_id},
            )
            raise ConflictException("National ID already registered")

        clinic = self.clinic_repository.get_by_id(request.clinic_id)
        if not clinic:
            logger.warning(
                "Register doctor failed: Clinic not found",
                extra={"clinic_id": str(request.clinic_id)},
            )
            raise NotFoundException("Clinic not found")

        # Transaction phase - create user and profile atomically
        password_hash = hash_password(request.password)
        user = UserModel(
            national_id=request.national_id,
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            phone_number=request.phone_number,
            password_hash=password_hash,
            date_of_birth=request.date_of_birth,
            gender=request.gender,
            role=RoleEnum.doctor,  # KEY: Set role to doctor
        )

        # Add user to session and flush to get ID without committing
        self.user_repository.db.add(user)
        self.user_repository.db.flush()

        # Create doctor profile
        profile = DoctorProfile(
            id=user.id,  # FK to user
            clinic_id=request.clinic_id,
            specialty=request.specialty,
        )

        # Add profile and commit both together
        self.doctor_profile_repository.db.add(profile)
        self.user_repository.db.commit()

        # Refresh to get relationships
        self.user_repository.db.refresh(user)

        # Generate tokens
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        # Get full profile with relationships
        full_profile = self.doctor_profile_repository.get_by_id_with_relations(user.id)

        logger.info(
            "Doctor registered successfully",
            extra={
                "user_id": str(user.id),
                "role": user.role.value,
                "clinic_id": str(request.clinic_id),
                "specialty": request.specialty,
            },
        )

        # Manually construct DoctorProfileResponse from related models
        doctor_profile_response = DoctorProfileResponse(
            id=full_profile.id,
            first_name=full_profile.user.first_name,
            last_name=full_profile.user.last_name,
            specialty=full_profile.specialty,
            hospital_id=full_profile.clinic.hospital_id,
            hospital_name=full_profile.clinic.hospital.name,
            clinic_id=full_profile.clinic_id,
            clinic_name=full_profile.clinic.name,
        )

        return RegisterDoctorResponse(
            user=UserResponse.model_validate(user),
            doctor_profile=doctor_profile_response,
            access_token=access_token,
            refresh_token=refresh_token,
        )
