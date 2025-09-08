from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.services.performance import plans_performance, year_performance

router = APIRouter(tags=["performance"])

@router.get("/plans_performance")
def get_plans_performance(date_: date = Query(..., alias="date"), db: Session = Depends(get_db)):
    return plans_performance(db, date_)


@router.get("/year_performance")
def get_year_performance(year: int, db: Session = Depends(get_db)):
    return year_performance(db, year)
