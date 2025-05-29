from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: str
    gender: str
    date_of_birth: Optional[date] = None

class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None

    class Config:
        orm_mode = True
