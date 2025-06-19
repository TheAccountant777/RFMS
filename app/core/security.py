from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError

from app.config import settings

# Algorithm for JWT
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Creates a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Default expiry time (e.g., 15 minutes)
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """Verifies a JWT token and returns the payload."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        # Invalid token or signature
        return None

# Note: You might also want functions for creating refresh tokens and password hashing here.
# Password hashing is typically handled by passlib.