# app/schemas/auth.py

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal

class LoginRequestSchema(BaseModel):
    username: str
    password: Optional[str] = None
    # This field dictates the type of login request
    # "userme" for initial validation, None/omitted for final authentication
    # validate: Optional[Literal["username"]] = None 
    request_type: Optional[Literal["validate_user"]] = None

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "summary": "Initial Validation Request (Step 1)",
                    "value": {
                        "username": "user@example.com",
                        "validate": "userme"
                    }
                },
                {
                    "summary": "Final Authentication Request (Step 2)",
                    "value": {
                        "username": "user@example.com",
                        "password": "StrongPassword123!"
                    }
                }
            ]
        }