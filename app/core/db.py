from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings


class Base(DeclarativeBase):
    pass

engine = create_engine(settings.DB_DSN, pool_recycle=3600, future=True, echo=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


import app.models
