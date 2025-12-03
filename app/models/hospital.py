from sqlalchemy import Column, String, Integer
from app.db.base import Base


class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    address = Column(String(255), nullable=False)
    city = Column(String(50), nullable=False)
    district = Column(String(50), nullable=False)
    phone = Column(String(20), nullable=False)
