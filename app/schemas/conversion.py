from pydantic import BaseModel, Field
from decimal import Decimal # For financial values

# --- Specific API Payloads (from TDD 2.1) ---

# Schema for conversion payload from Main SaaS platform
class ConversionPayload(BaseModel):
    referred_user_id: str = Field(..., description="The user's unique ID from the Main SaaS DB.")
    payment_amount: Decimal = Field(..., gt=0, decimal_places=2, description="The positive decimal value of the payment made.") # Use Decimal and validation
    transaction_id: str = Field(..., description="The unique transaction ID from the main platform's payment processor for idempotency.")
