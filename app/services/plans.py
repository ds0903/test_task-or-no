from datetime import date
from decimal import Decimal
import pandas as pd
from sqlalchemy import select, and_, func
from sqlalchemy.orm import Session
from app.models.plan import Plan
from app.models.dictionary import Dictionary


class PlansInsertError(Exception): ...


def _ensure_first_day(d: date):
    if d.day != 1:
        raise PlansInsertError("Період має бути першим числом місяця")

def insert_plans_from_excel(db: Session, file_bytes: bytes):
    df = pd.read_excel(file_bytes)

    for col in ("period", "category_name", "sum"):
        if col not in df.columns:
            raise PlansInsertError(f"Відсутня колонка: {col}")

    df["period"] = pd.to_datetime(df["period"]).dt.date
    df["category_name"] = (df["category_name"].astype(str).str.strip().str.lower())

    if df["sum"].isna().any():
        raise PlansInsertError("Колонка 'sum' містить порожні значення")
    if df["category_name"].eq("").any():
        raise PlansInsertError("Є порожні назви категорій")

    for d in df["period"]:
        _ensure_first_day(d)

    names = sorted(set(df["category_name"]))

    cats = (
        db.execute(
            select(Dictionary).where(func.lower(Dictionary.name).in_(names))
        )
        .scalars()
        .all()
    )
    name2id = {c.name.lower(): c.id for c in cats}

    missing = [n for n in names if n not in name2id]
    if missing:
        raise PlansInsertError(f"Невідомі категорії: {', '.join(missing)}")

    for _, row in df.iterrows():
        exists = db.execute(
            select(Plan.id).where(
                and_(
                    Plan.period == row["period"],
                    Plan.category_id == name2id[row["category_name"]],
                )
            )
        ).first()
        if exists:
            raise PlansInsertError("Дубль плану за період/категорією. Перевірте дані.") from e

    to_add = [
        Plan(
            period=row["period"],
            category_id=name2id[row["category_name"]],
            sum=Decimal(str(row["sum"])),
        )
        for _, row in df.iterrows()
    ]
    db.add_all(to_add)
    return {"inserted": len(to_add)}
