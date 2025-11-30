from sqlalchemy import Column, String, Date, Enum, Integer
from app.db.base import Base
import enum


class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"


class RoleEnum(str, enum.Enum):
    admin = "admin"
    doctor = "doctor"
    patient = "patient"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nationalId = Column(String(11), unique=True, index=True, nullable=False)
    firstName = Column(String(50), nullable=False)
    lastName = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phoneNumber = Column(String(20), nullable=False)
    passwordHash = Column(String(255), nullable=False)
    dateOfBirth = Column(Date, nullable=False)
    gender = Column(Enum(GenderEnum), nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.patient, nullable=False)
