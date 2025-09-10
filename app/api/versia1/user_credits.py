from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Union

from app.api.deps import get_db
from app.services.user_credits import get_user_credits
from app.schemas.user_credits import CreditOpen, CreditClosed

router = APIRouter(tags=["credits"])


@router.get(
    "/user_credits/{user_id}",
    response_model=List[Union[CreditOpen, CreditClosed]],
)
def user_credits(user_id: int, db: Session = Depends(get_db)):
    credits = get_user_credits(db, user_id)
    if credits is None or len(credits) == 0:
        raise HTTPException(status_code=404, detail=f"Для користувача {user_id} кредити не знайдено")

    # return {
    #     "user_id": user_id,
    #     "credits": credits,
    #     "count": len(credits),
    # }
    return credits