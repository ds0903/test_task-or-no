from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base
from sqlalchemy import ForeignKey, Numeric
from decimal import Decimal
from datetime import date


class Payment(Base):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(primary_key=True)

    sum: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    payment_date: Mapped[date]
    credit_id: Mapped[int] = mapped_column(ForeignKey("credits.id"), index=True)
    type_id: Mapped[int] = mapped_column(ForeignKey("dictionary.id"), index=True)
