import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.models.password_reset_request import PasswordResetRequestModel


class PasswordResetRequestRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, request: PasswordResetRequestModel) -> PasswordResetRequestModel:
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        return request

    def get_by_id(self, request_id: uuid.UUID) -> Optional[PasswordResetRequestModel]:
        return (
            self.db.query(PasswordResetRequestModel)
            .filter(PasswordResetRequestModel.id == request_id)
            .first()
        )

    def get_active_by_user(
        self, user_id: uuid.UUID
    ) -> Optional[PasswordResetRequestModel]:
        """Get the most recent active (not used, not expired) request for a user"""
        now = datetime.utcnow()
        return (
            self.db.query(PasswordResetRequestModel)
            .filter(
                PasswordResetRequestModel.user_id == user_id,
                PasswordResetRequestModel.used_at.is_(None),
                PasswordResetRequestModel.expires_at > now,
            )
            .order_by(PasswordResetRequestModel.created_at.desc())
            .first()
        )

    def update(self, request: PasswordResetRequestModel) -> PasswordResetRequestModel:
        self.db.commit()
        self.db.refresh(request)
        return request

    def mark_as_used(self, request: PasswordResetRequestModel) -> None:
        request.used_at = datetime.utcnow()
        self.db.commit()

    def increment_attempt(self, request: PasswordResetRequestModel) -> None:
        request.attempt_count += 1
        self.db.commit()

    def increment_resend(self, request: PasswordResetRequestModel) -> None:
        request.resend_count += 1
        self.db.commit()

    def get_verified_unused_requests(self) -> list[PasswordResetRequestModel]:
        """Get all verified but not yet used reset requests that haven't expired"""
        now = datetime.utcnow()
        return (
            self.db.query(PasswordResetRequestModel)
            .filter(
                PasswordResetRequestModel.verified_at.isnot(None),
                PasswordResetRequestModel.used_at.is_(None),
                PasswordResetRequestModel.expires_at > now,
            )
            .all()
        )
