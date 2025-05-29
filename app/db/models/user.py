from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, BigInteger, Date, Text
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(255), nullable=False)
    middle_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=False)
    suffix = Column(String(50), nullable=True)
    gender = Column(String(2), default="M")
    email = Column(String(254), unique=True, nullable=True)
    is_email_verified = Column(Boolean, default=False)
    phone_number = Column(String(12), nullable=False)
    phone_number_type = Column(String(10), default="CELL")
    secondary_phone_number = Column(String(12), nullable=True)
    secondary_phone_number_type = Column(String(12), default="LANDLINE")
    is_phone_number_used_for_sms = Column(Boolean, default=True)
    is_secondary_phone_number_used_for_sms = Column(Boolean, default=False)
    image = Column(Text, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    is_two_factor_enabled = Column(Boolean, default=False)
    created_at = Column(BigInteger)
    updated_at = Column(BigInteger, nullable=True)
    is_removed = Column(Boolean, default=False)
    is_test_account = Column(Boolean, default=False)
    account_status = Column(String(25), default="ACTIVE")
