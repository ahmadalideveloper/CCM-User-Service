from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.user_service import create_user
from app.schemas.user import UserCreateSchema, UserResponseSchema

router = APIRouter()

@router.post("/register", response_model=UserResponseSchema)
def register_user(user_in: UserCreateSchema, db: Session = Depends(get_db)):
    return create_user(db, user_in)
