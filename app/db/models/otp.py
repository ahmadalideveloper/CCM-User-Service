# app/db/models/otp.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
from app.db.models.base import BaseModelMixin # Assuming your Base and BaseModelMixin

class OTPCode(Base, BaseModelMixin):
    __tablename__ = "otp_codes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    otp_code = Column(String(6), nullable=False) # Assuming 6-digit OTP
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)

    # Relationship to User model
    user = relationship("User")

    def is_valid(self):
        """Checks if the OTP is not used and not expired."""
        return not self.is_used and self.expires_at > func.now()

    def mark_as_used(self):
        """Marks the OTP as used."""
        self.is_used = True
        self.updated_at = func.now() # Update the timestamp