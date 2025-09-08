from datetime import date
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.credit import Credit
from app.models.payment import Payment
from app.core.db import SessionLocal
from app.models.dictionary import Dictionary

payment_type_ids = None

def _get_payment_type_ids():
    with SessionLocal() as db:
        body_id = db.scalar(
            select(Dictionary.id).where(func.lower(Dictionary.name) == "тіло")
        )
        percent_id = db.scalar(
            select(Dictionary.id).where(func.lower(Dictionary.name) == "відсотки")
        )
        if body_id is None or percent_id is None:
            raise RuntimeError("Не знайдено типів 'Тіло'/'Відсотки' у dictionary")
        return body_id, percent_id

body_type_id, percent_type_id = _get_payment_type_ids()

def sum_payments(db: Session, credit_ids: list, type_name: str = None):

    if not credit_ids:
        return {}
    q = (
        select(Payment.credit_id, func.coalesce(func.sum(Payment.sum), 0))
        .where(Payment.credit_id.in_(credit_ids))
        .group_by(Payment.credit_id)
    )
    if type_name:
        q = q.join(Dictionary, Dictionary.id == Payment.type_id).where(Dictionary.name == type_name)
    rows = db.execute(q).all()
    return {cid: Decimal(total) for cid, total in rows}


def get_user_credits(db, user_id: int):
    credits = db.execute(
        select(Credit).where(Credit.user_id == user_id).order_by(Credit.issuance_date)
    ).scalars().all()

    items = []
    for c in credits:
        # if c.actual_return_date != 0000-00-00:
        if c.actual_return_date:
            payments_total = db.execute(
                select(func.coalesce(func.sum(Payment.sum), 0))
                .where(Payment.credit_id == c.id)
            ).scalar_one()
            items.append({
                "issuance_date": c.issuance_date,
                "closed": True,
                "actual_return_date": c.actual_return_date,
                "body": c.body,
                "percent": c.percent,
                "payments_total": payments_total,
            })
        else:
            payments = db.execute(
                select(Payment).where(Payment.credit_id == c.id)
            ).scalars().all()

            pay_body = sum(p.sum for p in payments if p.type_id == body_type_id)
            pay_percent = sum(p.sum for p in payments if p.type_id == percent_type_id)

            overdue = max((date.today() - c.return_date).days, 0)
            items.append({
                "issuance_date": c.issuance_date,
                "closed": False,
                "return_date": c.return_date,
                "overdue_days": overdue,
                "body": c.body,
                "percent": c.percent,
                "payments_body": pay_body,
                "payments_percent": pay_percent,
            })
    return items
