# app/schemas/auth.py

from pydantic import BaseModel, EmailStr, Field

class LoginRequestSchema(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., min_length=6, example="securepassword")
