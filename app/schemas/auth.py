from pydantic import BaseModel, Field, EmailStr
from typing import Optional

# --- Auth Payloads ---

# Schema for participant registration payload (from TDD 2.2)
class ParticipantRegisterPayload(BaseModel):
    full_name: str
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long.")
    phone_number: str = Field(..., description="Must be a valid Kenyan mobile number format.") # Add custom validator

# Schema for login payload (from TDD 2.3)
class LoginPayload(BaseModel):
    email: EmailStr
    password: str

# Schema for refresh token payload (from TDD 2.4)
class RefreshPayload(BaseModel):
    refresh_token: str

# --- Auth Responses ---

# Schema for JWT tokens response (from TDD 2.3, 2.4)
class JWTTokens(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None # Refresh token included only in initial login
    token_type: str = "bearer"
