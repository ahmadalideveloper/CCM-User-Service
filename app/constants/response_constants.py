# app/constants/response_constants.py

from fastapi import status

# Success Messages
SUCCESS_LOGIN = "Login successful"

# Error Messages
ERROR_INVALID_CREDENTIALS = "Invalid credentials"
ERROR_USER_NOT_FOUND = "User not found"
ERROR_MISSING_FIELDS = "Missing required fields"

# Error Codes
AUTH_FAILED = "AUTH_FAILED"
USER_NOT_FOUND = "USER_NOT_FOUND"
VALIDATION_ERROR = "VALIDATION_ERROR"
