from datetime import date
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

class CreditClosed(BaseModel):
    issuance_date: date
    closed: bool = True
    actual_return_date: date

    body: Decimal
    percent: Decimal
    payments_total: Decimal

    model_config = ConfigDict(from_attributes=True)

class CreditOpen(BaseModel):
    issuance_date: date
    closed: bool = False
    return_date: date
    overdue_days: int

    body: Decimal
    percent: Decimal
    payments_body: Decimal
    payments_percent: Decimal

    model_config = ConfigDict(from_attributes=True)
