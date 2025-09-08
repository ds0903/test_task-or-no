from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.services.plans import insert_plans_from_excel, PlansInsertError

router = APIRouter(tags=["plans"])

@router.post("/plans_insert")
async def plans_insert(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith((".xlsx",".xls")):
        raise HTTPException(status_code=400, detail="Лише Excel файли!!!!!")
    data = await file.read()
    try:
        res = insert_plans_from_excel(db, data)
    except PlansInsertError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "ok", **res}
