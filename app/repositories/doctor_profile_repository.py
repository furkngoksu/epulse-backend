import uuid
from sqlalchemy.orm import Session, joinedload
from app.models.doctor_profile import DoctorProfile
from app.models.clinic import Clinic


class DoctorProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> list[DoctorProfile]:
        return (
            self.db.query(DoctorProfile)
            .options(
                joinedload(DoctorProfile.user),
                joinedload(DoctorProfile.clinic).joinedload(Clinic.hospital),
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_id(self, profile_id: uuid.UUID) -> DoctorProfile | None:
        return (
            self.db.query(DoctorProfile)
            .options(
                joinedload(DoctorProfile.user),
                joinedload(DoctorProfile.clinic).joinedload(Clinic.hospital),
            )
            .filter(DoctorProfile.id == profile_id)
            .first()
        )

    def get_by_id_with_relations(self, profile_id: uuid.UUID) -> DoctorProfile | None:
        return (
            self.db.query(DoctorProfile)
            .options(
                joinedload(DoctorProfile.user),
                joinedload(DoctorProfile.clinic).joinedload(Clinic.hospital),
            )
            .filter(DoctorProfile.id == profile_id)
            .first()
        )

    def get_by_user_id(self, user_id: uuid.UUID) -> DoctorProfile | None:
        return self.db.query(DoctorProfile).filter(DoctorProfile.id == user_id).first()

    def get_by_clinic_id(self, clinic_id: uuid.UUID) -> list[DoctorProfile]:
        return (
            self.db.query(DoctorProfile)
            .options(
                joinedload(DoctorProfile.user),
                joinedload(DoctorProfile.clinic).joinedload(Clinic.hospital),
            )
            .filter(DoctorProfile.clinic_id == clinic_id)
            .all()
        )

    def create(self, profile: DoctorProfile) -> DoctorProfile:
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def update(self, profile: DoctorProfile) -> DoctorProfile:
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def delete(self, profile: DoctorProfile) -> None:
        self.db.delete(profile)
        self.db.commit()
