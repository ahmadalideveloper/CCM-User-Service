# app/exceptions/api_exception.py

from fastapi import HTTPException

class APIException(HTTPException):
    def __init__(self, message: str, error_code: str = None, status_code: int = 400, data=None):
        super().__init__(
            status_code=status_code,
            detail={
                "status": "error",
                "message": message,
                "error_code": error_code,
                "data": data,
            },
        )
