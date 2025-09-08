from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base
from sqlalchemy import ForeignKey, Date, Numeric
from datetime import date
from decimal import Decimal



class Plan(Base):
    __tablename__ = "plans"
    id: Mapped[int] = mapped_column(primary_key=True)
    period: Mapped[date]
    sum: Mapped [Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("dictionary.id"))
