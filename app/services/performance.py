from datetime import date
from decimal import Decimal
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session
from app.models.plan import Plan
from app.models.dictionary import Dictionary
from app.models.credit import Credit
from app.models.payment import Payment

def month_first(d: date) -> date:
    return d.replace(day=1)


def plans_performance(db: Session, as_of: date):
    period = month_first(as_of)

    plans = db.execute(
        select(Plan.id, Plan.sum, Dictionary.name.label("category"))
        .join(Dictionary, Dictionary.id == Plan.category_id)
        .where(Plan.period == period)
        .order_by(Dictionary.name)
    ).all()

    out = []
    for pid, plan_sum, category in plans:
        cat = (category or "").strip().lower()

        if cat == "видача":
            actual = db.execute(
                select(func.coalesce(func.sum(Credit.body), 0))
                .where(and_(
                    Credit.issuance_date >= period,
                    Credit.issuance_date <= as_of
                ))
            ).scalar_one()
        elif cat == "збір":
            actual = db.execute(
                select(func.coalesce(func.sum(Payment.sum), 0))
                .where(and_(
                    Payment.payment_date >= period,
                    Payment.payment_date <= as_of
                ))
            ).scalar_one()
        else:
            actual = 0

        plan_sum = Decimal((plan_sum or 0))
        actual = Decimal((actual or 0))
        pct = float(actual / plan_sum * 100) if plan_sum != 0 else (100.0 if actual == 0 else 0.0)

        out.append({
            "period": period,
            "category": category,
            "plan_sum": plan_sum,
            "actual_sum": actual,
            "plan_completion_pct": round(pct, 2),
        })
    return out


def year_performance(db: Session, year: int):
    from collections import defaultdict



    plans_rows = db.execute(
        select(Plan.period, Dictionary.name, func.coalesce(func.sum(Plan.sum), 0).label("sum"))
        .join(Dictionary, Dictionary.id == Plan.category_id)
        .where(func.extract("year", Plan.period) == year)
        .group_by(Plan.period, Dictionary.name)
    ).all()

    credits_rows = db.execute(
        select(Credit.issuance_date, func.count(Credit.id), func.coalesce(func.sum(Credit.body), 0))
        .where(func.extract("year", Credit.issuance_date) == year)
        .group_by(Credit.issuance_date)
    ).all()

    payments_rows = db.execute(
        select(Payment.payment_date, func.count(Payment.id), func.coalesce(func.sum(Payment.sum), 0))
        .where(func.extract("year", Payment.payment_date) == year)
        .group_by(Payment.payment_date)
    ).all()

    def ym(d): return (d.year, d.month)

    agg = defaultdict(lambda: {
        "month": None, "year": year,
        "issue_count": 0, "issue_plan_sum": Decimal("0"), "issue_sum": Decimal("0"),
        "issue_plan_completion_pct": 0.0,
        "payment_count": 0, "collect_plan_sum": Decimal("0"), "payment_sum": Decimal("0"),
        "collect_plan_completion_pct": 0.0,
        "issue_share_of_year_pct": 0.0, "payment_share_of_year_pct": 0.0,
    })

    for period, cat, s in plans_rows:
        key = ym(period)
        agg[key]["month"] = key[1]
        s = Decimal((s or 0))
        if cat == "видача":
            agg[key]["issue_plan_sum"] += s
        elif cat == "збір":
            agg[key]["collect_plan_sum"] += s

    for d, cnt, s in credits_rows:
        key = ym(d)
        agg[key]["month"] = key[1]
        agg[key]["issue_count"] += int(cnt or 0)
        agg[key]["issue_sum"] += Decimal((s or 0))

    for d, cnt, s in payments_rows:
        key = ym(d)
        agg[key]["month"] = key[1]
        agg[key]["payment_count"] += int(cnt or 0)
        agg[key]["payment_sum"] += Decimal((s or 0))

    total_issue = sum(v["issue_sum"] for v in agg.values())
    total_payment = sum(v["payment_sum"] for v in agg.values())

    out = []
    for m in range(1, 13):
        key = (year, m)
        v = agg[key]
        issue_plan = v["issue_plan_sum"]
        collect_plan = v["collect_plan_sum"]
        issue = v["issue_sum"]
        pay = v["payment_sum"]

        v["issue_plan_completion_pct"] = float(issue / issue_plan * 100) if issue_plan != 0 else (100.0 if issue == 0 else 0.0)
        v["collect_plan_completion_pct"] = float(pay / collect_plan * 100) if collect_plan != 0 else (100.0 if pay == 0 else 0.0)
        v["issue_share_of_year_pct"] = float(issue / total_issue * 100) if total_issue != 0 else 0.0
        v["payment_share_of_year_pct"] = float(pay / total_payment * 100) if total_payment != 0 else 0.0
        v["month"] = m
        out.append(v)

    return out
