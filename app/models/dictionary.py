from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base
from sqlalchemy import String


class Dictionary(Base):
    __tablename__ = "dictionary"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True)
