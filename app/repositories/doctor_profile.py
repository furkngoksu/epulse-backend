from sqlalchemy.orm import Session, joinedload
from uuid import UUID
from app.models.doctor_profile import DoctorProfile


class DoctorProfileRepository:

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[DoctorProfile]:
        return db.query(DoctorProfile).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, profile_id: UUID) -> DoctorProfile | None:
        return db.query(DoctorProfile).filter(DoctorProfile.id == profile_id).first()

    @staticmethod
    def get_by_id_with_relations(db: Session, profile_id: UUID) -> DoctorProfile | None:
        return (
            db.query(DoctorProfile)
            .options(joinedload(DoctorProfile.user), joinedload(DoctorProfile.hospital))
            .filter(DoctorProfile.id == profile_id)
            .first()
        )

    @staticmethod
    def get_by_user_id(db: Session, user_id: UUID) -> DoctorProfile | None:
        return db.query(DoctorProfile).filter(DoctorProfile.id == user_id).first()

    @staticmethod
    def get_by_hospital_id(db: Session, hospital_id: UUID) -> list[DoctorProfile]:
        return db.query(DoctorProfile).filter(DoctorProfile.hospital_id == hospital_id).all()

    @staticmethod
    def create(db: Session, profile: DoctorProfile) -> DoctorProfile:
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def update(db: Session, profile: DoctorProfile) -> DoctorProfile:
        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def delete(db: Session, profile: DoctorProfile) -> None:
        db.delete(profile)
        db.commit()
