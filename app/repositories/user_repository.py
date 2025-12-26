import uuid
from sqlalchemy.orm import Session
from app.models.user import UserModel, RoleEnum


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> UserModel | None:
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    def get_by_national_id(self, national_id: str) -> UserModel | None:
        return (
            self.db.query(UserModel)
            .filter(UserModel.national_id == national_id)
            .first()
        )

    def get_by_id(self, user_id: uuid.UUID) -> UserModel | None:
        return self.db.query(UserModel).filter(UserModel.id == user_id).first()

    def get_users(self, skip=0, limit=100):
        return self.db.query(UserModel).offset(skip).limit(limit).all()

    def create(self, user: UserModel) -> UserModel:
        # Convert enums to lowercase before saving
        if isinstance(user.role, RoleEnum):
            user.role = RoleEnum(user.role.value.lower())
        elif isinstance(user.role, str):
            user.role = RoleEnum(user.role.lower())

        if hasattr(user, 'gender') and user.gender:
            from app.models.user import GenderEnum
            if isinstance(user.gender, GenderEnum):
                user.gender = GenderEnum(user.gender.value.lower())
            elif isinstance(user.gender, str):
                user.gender = GenderEnum(user.gender.lower())

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: UserModel) -> UserModel:
        # Convert enums to lowercase before saving
        if isinstance(user.role, RoleEnum):
            user.role = RoleEnum(user.role.value.lower())
        elif isinstance(user.role, str):
            user.role = RoleEnum(user.role.lower())

        if hasattr(user, 'gender') and user.gender:
            from app.models.user import GenderEnum
            if isinstance(user.gender, GenderEnum):
                user.gender = GenderEnum(user.gender.value.lower())
            elif isinstance(user.gender, str):
                user.gender = GenderEnum(user.gender.lower())

        self.db.merge(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_total_count(self) -> int:
        return self.db.query(UserModel).count()

    def get_count_by_role(self, role: RoleEnum) -> int:
        return self.db.query(UserModel).filter(UserModel.role == role).count()
