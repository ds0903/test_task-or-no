from sqlalchemy import ForeignKey, Date, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base
from datetime import date
from decimal import Decimal



class Credit(Base):
    __tablename__ = "credits"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    issuance_date: Mapped[date]
    return_date: Mapped[date]
    actual_return_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    body: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    percent: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    user = relationship("User")