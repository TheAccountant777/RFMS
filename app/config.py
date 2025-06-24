from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Uses pydantic-settings for validation and loading.
    """
    project_name: str = "Jijenga Referral System"
    database_url: Optional[str] = None
    jwt_secret_key: str = "test-secret-key-for-development-only-change-in-production"
    mpesa_api_key: Optional[str] = None
    resend_api_key: Optional[str] = None
    referral_base_url: str = "http://localhost:8000"
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='allow',  # Allow extra fields to prevent validation errors
        case_sensitive=False,
        env_ignore_empty=True,
        validate_assignment=True
    )

# Create settings instance
settings = Settings()