from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
import re

# --- Auth Payloads ---

# Schema for participant registration payload (from TDD 2.2)
class ParticipantRegisterPayload(BaseModel):
    full_name: str
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long.")
    phone_number: str = Field(..., description="Must be a valid Kenyan mobile number format.")
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v):
        # Validate Kenyan phone number format (e.g., +254712345678)
        pattern = r'^\+254[7,1][0-9]{8}$'
        if not re.match(pattern, v):
            raise ValueError("Phone number must be in valid Kenyan format (e.g., +254712345678)")
        return v

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
