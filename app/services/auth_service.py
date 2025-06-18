# app/services/auth_service.py

from app.db.models.user import User  # your SQLAlchemy User model
from app.db.session import get_db
from sqlalchemy.orm import Session
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

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
