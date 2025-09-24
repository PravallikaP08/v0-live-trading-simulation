from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings

engine = create_engine(
  settings.database_url, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


def init_db() -> None:
  # Import models to ensure metadata is registered before create_all
  from . import models  # noqa: F401

  Base.metadata.create_all(bind=engine)
