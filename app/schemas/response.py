# app/schemas/response.py

from typing import Optional, Any
from pydantic import BaseModel

class SuccessResponse(BaseModel):
    status: str = "success"
    message: str
    data: Optional[Any] = None

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    error_code: Optional[str] = None
    data: Optional[Any] = None
