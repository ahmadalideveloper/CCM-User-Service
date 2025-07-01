# app/services/auth_service.py

from app.db.models.user import User  # your SQLAlchemy User model
from app.db.session import get_db
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from jose import jwt
from app.services import otp_service
from app.core.config import settings
from app.core.security import pwd_context
from app.db.models.role import Role # Assuming User has a relationship to Role
from concurrent.futures import ThreadPoolExecutor # For run_in_threadpool
import functools
import asyncio


# Global thread pool for CPU-bound tasks like password hashing
executor = ThreadPoolExecutor()

# Helper to run blocking code in a thread pool (for FastAPI's async nature)
def run_in_threadpool(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(executor, functools.partial(func, *args, **kwargs))
    return wrapper



def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

@run_in_threadpool
def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = db.query(User).filter(User.username == username, User.is_removed == False).first()
    if not user:
        # Compare against a dummy hash or just hash the input password to
        # take roughly the same amount of time as a real comparison.
        # Generate a hash for a dummy string (e.g., an empty string)
        DUMMY_HASH = pwd_context.hash("") # This will produce a valid bcrypt hash
        pwd_context.verify(password, DUMMY_HASH) # A dummy hash
        return None
    
    if not verify_password(password, user.password):
        return None
    return user

# --- New function for initial login validation ---
# @run_in_threadpool # Apply this decorator if your FastAPI endpoint is async
async def handle_initial_login_validation(db: Session, username: str) -> Dict[str, Any]:
    """
    Handles the initial login validation step (username/email check).
    Sends OTP if it's the user's first login.
    """
    username = str(username).lower()
    
    user = db.query(User).filter(User.email == username).first()
    email = None
    if user:
        email = user.email

    response_data = {
        "email": email,
        "is_first_login": False, # Default to false
        "otp_sent": False
    }

    if user:
        if not user.is_removed: # Consider only active, non-removed users for this check
            response_data["is_first_login"] = not user.is_first_login_completed

            if not user.is_first_login_completed:
                # Generate and store OTP
                otp_code = otp_service.create_and_store_otp(db, user)
                # Send OTP email (this is an async operation)
                await otp_service.send_otp_email(user.email, otp_code)
                response_data["otp_sent"] = True
            
            # If user exists and is not first login, otp_sent remains False, is_first_login is False
        else:
            # User exists but is removed or inactive.
            # We still return 200 OK but effectively treat it like user not found
            # from a login perspective to prevent enumeration.
            pass # Default response_data is fine.
    else:
        # User not found. Adhere to "no matter user exist or not user moves to password screen"
        pass # Default response_data is fine.

    return response_data