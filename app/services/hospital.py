from sqlalchemy.orm import Session
from uuid import UUID

from app.models.hospital import Hospital
from app.repositories.hospital import HospitalRepository
from app.schemas.hospital import HospitalCreate, HospitalUpdate
from app.exceptions.exceptions import NotFoundException


class HospitalService:

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Hospital]:
        return HospitalRepository.get_all(db, skip=skip, limit=limit)

    @staticmethod
    def get_by_id(db: Session, hospital_id: UUID) -> Hospital:
        hospital = HospitalRepository.get_by_id(db, hospital_id)
        if not hospital:
            raise NotFoundException("Hospital not found")
        return hospital

    @staticmethod
    def create(db: Session, data: HospitalCreate) -> Hospital:
        hospital = Hospital(
            name=data.name,
            address=data.address,
            city=data.city,
            district=data.district,
            phone=data.phone
        )
        return HospitalRepository.create(db, hospital)

    @staticmethod
    def update(db: Session, hospital_id: UUID, data: HospitalUpdate) -> Hospital:
        hospital = HospitalRepository.get_by_id(db, hospital_id)
        if not hospital:
            raise NotFoundException("Hospital not found")

        # Update only provided fields
        if data.name is not None:
            hospital.name = data.name
        if data.address is not None:
            hospital.address = data.address
        if data.city is not None:
            hospital.city = data.city
        if data.district is not None:
            hospital.district = data.district
        if data.phone is not None:
            hospital.phone = data.phone

        return HospitalRepository.update(db, hospital)

    @staticmethod
    def delete(db: Session, hospital_id: UUID) -> None:
        hospital = HospitalRepository.get_by_id(db, hospital_id)
        if not hospital:
            raise NotFoundException("Hospital not found")
        HospitalRepository.delete(db, hospital)
