import pytest
from pydantic import ValidationError
from decimal import Decimal
from app.schemas.conversion import ConversionPayload

def test_conversion_payload_valid():
    """Test valid ConversionPayload."""
    data = {
        "referred_user_id": "user123",
        "payment_amount": "50.00", # Test string input for Decimal
        "transaction_id": "txn_abc123"
    }
    payload = ConversionPayload(**data)
    assert payload.referred_user_id == data["referred_user_id"]
    assert payload.payment_amount == Decimal(data["payment_amount"])
    assert payload.transaction_id == data["transaction_id"]

def test_conversion_payload_invalid_payment_amount_zero():
    """Test ConversionPayload with zero payment_amount."""
    data = {
        "referred_user_id": "user123",
        "payment_amount": "0.00", # Zero amount
        "transaction_id": "txn_abc123"
    }
    with pytest.raises(ValidationError) as exc_info:
        ConversionPayload(**data)
    assert "payment_amount" in str(exc_info.value)
    assert "greater than 0" in str(exc_info.value)

def test_conversion_payload_invalid_payment_amount_negative():
    """Test ConversionPayload with negative payment_amount."""
    data = {
        "referred_user_id": "user123",
        "payment_amount": "-10.00", # Negative amount
        "transaction_id": "txn_abc123"
    }
    with pytest.raises(ValidationError) as exc_info:
        ConversionPayload(**data)
    assert "payment_amount" in str(exc_info.value)
    assert "greater than 0" in str(exc_info.value)

def test_conversion_payload_invalid_payment_amount_type():
    """Test ConversionPayload with non-numeric payment_amount."""
    data = {
        "referred_user_id": "user123",
        "payment_amount": "fifty", # Invalid type
        "transaction_id": "txn_abc123"
    }
    with pytest.raises(ValidationError) as exc_info:
        ConversionPayload(**data)
    assert "payment_amount" in str(exc_info.value)
    assert "Input should be a valid decimal" in str(exc_info.value)


# TODO: Add tests for missing fields in ConversionPayload
