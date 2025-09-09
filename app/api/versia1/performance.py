from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.services.performance import plans_performance, year_performance

router = APIRouter(tags=["performance"])

@router.get("/plans_performance")
def get_plans_performance(
    date_: date = Query(..., alias="date", description="Дата для розрахунку"),
    db: Session = Depends(get_db),
):
    if not date_:
        return {"error": "Не вказано дату"}

    result = plans_performance(db, date_)
    return {"date": date_, "data": result}


@router.get("/year_performance")
def get_year_performance(
    year: int = Query(..., description="Рік, за який рахувати"),
    db: Session = Depends(get_db),
):
    if year < 2000 or year > date.today().year:
        return {"error": f"Некоректний рік: {year}"}

    data = year_performance(db, year)
    return {"year": year, "data": data}