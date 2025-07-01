# app/services/otp_service.py
import random
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
import os
import asyncio # Needed for async operations

# Make sure these imports point to your actual models
from app.db.models.user import User
from app.db.models.otp import OTPCode

# Mock settings for OTP expiry. In a real app, load from config.py (e.g., from settings.OTP_EXPIRY_MINUTES)
# For now, we'll use an environment variable or a default.
OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES", "5")) # Default to 5 minutes for demonstration

def generate_otp(length: int = 6) -> str:
    """Generates a random numeric OTP."""
    return ''.join(random.choices(string.digits, k=length))

async def send_otp_email(email: str, otp_code: str):
    """
    Mocks sending an OTP email.
    In a real application, integrate with an actual email sending service (e.g., SendGrid, Mailgun, aiosmtplib).
    This function should be asynchronous if your email sending library is async.
    """
    print(f"\n--- MOCK EMAIL SEND ---")
    print(f"To: {email}")
    print(f"Subject: Your One-Time Password (OTP)")
    print(f"Body: Your OTP for login is: {otp_code}. It is valid for {OTP_EXPIRY_MINUTES} minutes.")
    print(f"-------------------------\n")
    # Simulate network delay for an async operation
    await asyncio.sleep(1) # For demonstration purposes
    # Here you would typically call your email sending client, e.g.:
    # from your_email_client import EmailClient
    # email_client = EmailClient(...)
    # await email_client.send_email(
    #     to_email=email,
    #     subject="Your One-Time Password (OTP)",
    #     body=f"Your OTP for login is: {otp_code}. It is valid for {OTP_EXPIRY_MINUTES} minutes."
    # )

def create_and_store_otp(db: Session, user: User) -> str:
    """
    Generates and stores a new OTP for a user.
    Invalidates any existing active OTPs for the same user.
    """
    # Invalidate any existing active OTPs for this user to ensure only one is valid at a time
    db.query(OTPCode).filter(
        OTPCode.user_id == user.id,
        OTPCode.is_used == False,
        OTPCode.expires_at > func.now() # Only invalidate if not expired yet
    ).update({"is_used": True})
    db.commit()

    otp_code_str = generate_otp()
    expires_at = datetime.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)

    otp_entry = OTPCode(
        user_id=user.id,
        otp_code=otp_code_str,
        expires_at=expires_at
    )
    db.add(otp_entry)
    db.commit() # Commit to save the new OTP and invalidate old ones
    db.refresh(otp_entry) # Refresh to get the ID if needed later
    return otp_code_str

def verify_otp(db: Session, user_id: int, otp_code: str) -> bool:
    """
    Verifies an OTP for a given user.
    Marks the OTP as used if valid.
    """
    otp_entry = db.query(OTPCode).filter(
        OTPCode.user_id == user_id,
        OTPCode.otp_code == otp_code,
        OTPCode.is_used == False,
        OTPCode.expires_at > func.now() # Check if not expired
    ).first()

    if otp_entry:
        otp_entry.is_used = True
        # db.add(otp_entry) # No need to add, it's already managed by session
        db.commit() # Commit the change (is_used = True)
        return True
    return False