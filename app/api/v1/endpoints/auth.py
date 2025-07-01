from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.schemas.response import SuccessResponse, ErrorResponse
from app.schemas.auth import LoginRequestSchema
from app.constants import response_constants as rc
from app.services import auth_service
from app.db.session import get_db
from starlette.status import HTTP_401_UNAUTHORIZED
from app.exceptions.api_exception import APIException
from app.core.security import create_access_token
from starlette.concurrency import run_in_threadpool
from datetime import datetime, timedelta





router = APIRouter()

@router.post("/login", summary="User Login (Two-Step Process)",
             responses={
                 200: {"model": SuccessResponse, "description": "Success response for initial validation or token issuance"},
                 400: {"model": ErrorResponse, "description": "Bad Request"},
                 401: {"model": ErrorResponse, "description": "Unauthorized (for final authentication step)"}
             })
async def login(request: LoginRequestSchema, db: Session = Depends(get_db)):
    """
    Handles both initial username/email validation and final password-based authentication.

    **Initial Validation (Step 1):**
    - Payload: `{"username": "...", "validate": "userme"}`
    - Returns: Status of user (first-time login, OTP sent, etc.)

    **Final Authentication (Step 2):**
    - Payload: `{"username": "...", "password": "..."}`
    - Returns: Access token if credentials are valid.
    """
    
    # --- Step 1: Initial Validation & OTP Sending ---
    if request.request_type == "validate":
        if request.password is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorResponse(
                    message="Password not expected for initial validation step",
                    error_code="INVALID_REQUEST"
                ).model_dump()
            )
        
        # Call the new service function for initial validation
        result = await auth_service.handle_initial_login_validation(db, request.username)
        
        # Determine the message based on the result
        message = "Login initiation successful."
        if result.get("otp_sent"):
            message = "OTP sent to your email. Please proceed to login with password and OTP."
        elif result.get("is_first_login"): # User exists, first_login=True, but OTP not sent (e.g., already sent and valid)
            message = "Proceed to login with your password and OTP."
        else: # User exists (normal login) or user not found (to prevent enumeration)
            message = "Proceed to login with your password."
            
        return SuccessResponse(message=message, data=result)

    # --- Step 2: Final Authentication (Password Verification) ---
    else:
        # Password is required for the final authentication step
        if request.password is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorResponse(
                    message="Password is required for authentication step",
                    error_code="PASSWORD_REQUIRED"
                ).model_dump()
            )

        # Authenticate user with username/email and password
        user = await auth_service.authenticate_user(db, request.username, request.password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ErrorResponse(
                    message="Incorrect username or password.",
                    error_code="INVALID_CREDENTIALS"
                ).model_dump()
            )
        
        # If user is first-time login and reached here with just password, that's an issue.
        # However, per the flow, the frontend should prompt for OTP in a separate step before this.
        # This login endpoint handles only password verification now.
        # The OTP verification step will be a separate API (e.g. POST /auth/verify-otp)

        # Generate access token
        access_token_expires = timedelta(minutes=int(auth_service.settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id, "role_id": user.role.id}, # Include role_id from user.role.id
            expires_delta=access_token_expires
        )
        
        # Return success with token
        return SuccessResponse(
            message="Login successful",
            data={
                "access_token": access_token,
                "token_type": "bearer",
                "user_id": user.id,
                "email": user.email,
                "role_id": user.role.id,
                "is_first_login_completed": user.is_first_login_completed
            }
        )
