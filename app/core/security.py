from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
import secrets
import string

from app.config import settings

# Algorithm for JWT
ALGORITHM = "HS256"
# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Creates a JWT access token."""
    to_encode = data.copy()
    if "type" not in to_encode: # Ensure type is set, default to access
        to_encode["type"] = "access"
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Default expiry time (e.g., 15 minutes)
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Creates a JWT refresh token with longer expiry."""
    to_encode = data.copy()
    to_encode["type"] = "refresh" # Ensure type is set to refresh
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Default expiry time for refresh token (e.g., 7 days)
        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """Verifies a JWT token and returns the payload."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        # Invalid token or signature
        return None

def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def generate_unique_code(length: int = 8) -> str:
    """Generates a unique code for referral links."""
    # Use uppercase letters and digits for better readability
    alphabet = string.ascii_uppercase + string.digits
    # Exclude similar looking characters
    alphabet = alphabet.replace('O', '').replace('0', '').replace('I', '').replace('1', '')
    return ''.join(secrets.choice(alphabet) for _ in range(length))