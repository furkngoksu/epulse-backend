from app.db.session import engine
from app.db.base import Base

# Import all models so SQLAlchemy can create tables
from app.models import *  # noqa: F401, F403


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
