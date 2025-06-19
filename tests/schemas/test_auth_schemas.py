import pytest
from pydantic import ValidationError
from app.schemas.auth import ParticipantRegisterPayload, LoginPayload, RefreshPayload, JWTTokens

def test_participant_register_payload_valid():
    """Test valid ParticipantRegisterPayload."""
    data = {
        "full_name": "Test User",
        "password": "securepassword123",
        "phone_number": "+254712345678" # Assuming this format
    }
    payload = ParticipantRegisterPayload(**data)
    assert payload.full_name == data["full_name"]
    assert payload.password == data["password"]
    assert payload.phone_number == data["phone_number"]

def test_participant_register_payload_invalid_password_length():
    """Test ParticipantRegisterPayload with password too short."""
    data = {
        "full_name": "Test User",
        "password": "short", # Less than 8 characters
        "phone_number": "+254712345678"
    }
    with pytest.raises(ValidationError) as exc_info:
        ParticipantRegisterPayload(**data)
    assert "password" in str(exc_info.value)
    # Update assertion to match Pydantic V2+ error message format
    assert "String should have at least" in str(exc_info.value) # Check for the descriptive part
    # Alternative: assert "[type=string_too_short]" in str(exc_info.value) # Check for the error type code

# TODO: Add tests for invalid phone number format (requires custom validator)
# TODO: Add tests for missing fields in ParticipantRegisterPayload

def test_login_payload_valid():
    """Test valid LoginPayload."""
    data = {
        "email": "test@example.com",
        "password": "securepassword123"
    }
    payload = LoginPayload(**data)
    assert payload.email == data["email"]
    assert payload.password == data["password"]

# TODO: Add tests for invalid email format, missing fields in LoginPayload

def test_refresh_payload_valid():
    """Test valid RefreshPayload."""
    data = {
        "refresh_token": "a1b2c3d4e5f6"
    }
    payload = RefreshPayload(**data)
    assert payload.refresh_token == data["refresh_token"]

# TODO: Add tests for missing fields in RefreshPayload

def test_jwt_tokens_valid_login():
    """Test valid JWTTokens for initial login."""
    data = {
        "access_token": "eyJ...",
        "refresh_token": "a1b2...",
        "token_type": "bearer"
    }
    tokens = JWTTokens(**data)
    assert tokens.access_token == data["access_token"]
    assert tokens.refresh_token == data["refresh_token"]
    assert tokens.token_type == data["token_type"]

def test_jwt_tokens_valid_refresh():
    """Test valid JWTTokens for token refresh (no refresh_token)."""
    data = {
        "access_token": "eyJ...",
        "token_type": "bearer"
    }
    tokens = JWTTokens(**data)
    assert tokens.access_token == data["access_token"]
    assert tokens.refresh_token is None # Refresh token is optional
    assert tokens.token_type == data["token_type"]

# TODO: Add tests for missing access_token, token_type in JWTTokens
