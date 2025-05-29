from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas import user as user_schema, token as token_schema
from app.crud.user import get_user_by_email
from app.core.security import verify_password, create_access_token

router = APIRouter()

@router.post("/login", response_model=token_schema.Token)
def login(user_in: user_schema.UserCreate, db: Session = Depends(get_db)):
    user = get_user_by_email(db, email=user_in.email)
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"user_id": user.id})
    return {"access_token": token}
