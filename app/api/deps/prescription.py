from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.deps.db import get_db
from app.api.deps.auth import get_current_user
from app.models.user import UserModel

from app.repositories.prescription_repository import PrescriptionRepository
from app.repositories.prescription_item_repository import PrescriptionItemRepository
from app.services.prescription_service import PrescriptionService


def get_prescription_repository(
    db: Session = Depends(get_db),
) -> PrescriptionRepository:
    return PrescriptionRepository(db)


def get_prescription_item_repository(
    db: Session = Depends(get_db),
) -> PrescriptionItemRepository:
    return PrescriptionItemRepository(db)


def get_prescription_service(
    prescription_repository: PrescriptionRepository = Depends(get_prescription_repository),
    prescription_item_repository: PrescriptionItemRepository = Depends(get_prescription_item_repository),
    current_user: UserModel = Depends(get_current_user),
) -> PrescriptionService:
    return PrescriptionService(
        prescription_repository=prescription_repository,
        prescription_item_repository=prescription_item_repository,
        current_user=current_user,
    )
