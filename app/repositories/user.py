import uuid
from sqlalchemy.orm import Session
from app.models.user import UserModel


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> UserModel | None:
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    def get_by_national_id(self, national_id: str) -> UserModel | None:
        return self.db.query(UserModel).filter(UserModel.national_id == national_id).first()

    def get_by_id(self, user_id: uuid.UUID) -> UserModel | None:
        return self.db.query(UserModel).filter(UserModel.id == user_id).first()

    def create(self, user: UserModel) -> UserModel:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update(self, user: UserModel) -> UserModel:
        self.db.merge(user)
        self.db.commit()
        self.db.refresh(user)
        return user