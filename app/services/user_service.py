# app/services/user_service.py

from sqlalchemy.orm import Session
from app.db.models.user import User
from app.schemas.user import UserCreateSchema
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_user(db: Session, user_in: UserCreateSchema) -> User:
    hashed_password = hash_password(user_in.password)

    new_user = User(
        first_name=user_in.first_name,
        middle_name=user_in.middle_name,
        last_name=user_in.last_name,
        suffix=user_in.suffix,
        gender=user_in.gender,
        email=user_in.email,
        username=user_in.username,
        password=hashed_password,
        phone_number=user_in.phone_number,
        phone_number_type=user_in.phone_number_type,
        secondary_phone_number=user_in.secondary_phone_number,
        secondary_phone_number_type=user_in.secondary_phone_number_type,
        is_phone_number_used_for_sms=user_in.is_phone_number_used_for_sms,
        is_secondary_phone_number_used_for_sms=user_in.is_secondary_phone_number_used_for_sms,
        image=user_in.image,
        date_of_birth=user_in.date_of_birth,
        is_two_factor_enabled=user_in.is_two_factor_enabled,
        role_id=user_in.role_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        is_removed=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
