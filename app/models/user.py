from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from app.core.db import Base
from datetime import date


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    login: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    registration_date: Mapped[date]


    def __repr__(self) -> str:
        return f"<User id={self.id} login='{self.login}' registered={self.registration_date}>"