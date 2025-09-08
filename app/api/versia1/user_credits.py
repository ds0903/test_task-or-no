from fastapi import APIRouter, Depends
from app.api.deps import get_db
from app.services.user_credits import get_user_credits
from typing import List, Union
from app.schemas.user_credits import CreditOpen, CreditClosed

router = APIRouter(tags=["credits"])

@router.get("/user_credits/{user_id}",
            response_model=List[Union[CreditOpen, CreditClosed]])
def user_credits(user_id: int, db=Depends(get_db)):
    return get_user_credits(db, user_id)