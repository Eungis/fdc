from fastapi.params import Depends
from fastapi import APIRouter
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from project import schemas, models
from project.database import get_db

router = APIRouter(tags=["Seller"], prefix="/seller")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/", response_model=schemas.DisplaySeller)
def create_seller(request: schemas.Seller, db: Session = Depends(get_db)):
    hashed_pw = pwd_context.hash(request.password)
    new_seller = models.Seller(username=request.username, email=request.email, password=hashed_pw)
    db.add(new_seller)
    db.commit()
    db.refresh(new_seller)
    return new_seller
