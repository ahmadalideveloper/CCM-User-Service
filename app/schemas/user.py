# app/schemas/user.py

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime

class UserCreateSchema(BaseModel):
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    suffix: Optional[str] = None
    gender: Optional[str] = "M"
    email: Optional[EmailStr] = None
    username: str
    password: str
    phone_number: str
    phone_number_type: Optional[str] = "CELL"
    secondary_phone_number: Optional[str] = None
    secondary_phone_number_type: Optional[str] = "LANDLINE"
    is_phone_number_used_for_sms: Optional[bool] = True
    is_secondary_phone_number_used_for_sms: Optional[bool] = False
    image: Optional[str] = None
    date_of_birth: Optional[date] = None
    is_two_factor_enabled: Optional[bool] = False
    role_id: int

class UserResponseSchema(BaseModel):
    id: int
    first_name: str
    middle_name: Optional[str]
    last_name: str
    suffix: Optional[str]
    gender: Optional[str]
    email: Optional[EmailStr]
    username: str
    phone_number: str
    secondary_phone_number: Optional[str]
    image: Optional[str]
    date_of_birth: Optional[date]
    is_two_factor_enabled: bool
    role_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True  # ← use this instead of orm_mode
