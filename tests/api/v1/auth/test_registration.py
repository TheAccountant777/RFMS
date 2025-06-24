import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta
from unittest.mock import patch

from app.models.invitation import Invitation, InvitationStatus
from app.models.user import User
from app.models.referral_link import ReferralLink

@pytest.mark.asyncio
async def test_register_participant_success(client: AsyncClient, test_db):
    """Test successful registration with valid token."""
    # Create a test invitation in the database
    invitation = Invitation(
        email="test@example.com",
        token="valid_test_token",
        status=InvitationStatus.PENDING,
        expires_at=datetime.utcnow() + timedelta(days=1)
    )
    test_db.add(invitation)
    await test_db.commit()
    
    # Make the request
    response = await client.post(
        "/api/v1/auth/register?invitation_token=valid_test_token",
        json={
            "full_name": "Test User",
            "password": "password123",
            "phone_number": "+254712345678"
        }
    )
    
    # Assert response
    assert response.status_code == 201
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    
    # Verify database state
    # Check that user was created
    user_result = await test_db.execute("SELECT * FROM referral.users WHERE email = 'test@example.com'")
    user = user_result.fetchone()
    assert user is not None
    assert user.full_name == "Test User"
    assert user.phone_number == "+254712345678"
    
    # Check that referral link was created
    referral_link_result = await test_db.execute(f"SELECT * FROM referral.referral_links WHERE user_id = '{user.id}'")
    referral_link = referral_link_result.fetchone()
    assert referral_link is not None
    assert len(referral_link.unique_code) > 0
    
    # Check that invitation was marked as accepted
    invitation_result = await test_db.execute("SELECT * FROM referral.invitations WHERE token = 'valid_test_token'")
    invitation = invitation_result.fetchone()
    assert invitation.status == InvitationStatus.ACCEPTED.value

@pytest.mark.asyncio
async def test_register_invalid_token(client: AsyncClient):
    """Test registration with an invalid token."""
    response = await client.post(
        "/api/v1/auth/register?invitation_token=invalid_token",
        json={
            "full_name": "Test User",
            "password": "password123",
            "phone_number": "+254712345678"
        }
    )
    
    assert response.status_code == 404
    assert "Invalid or expired invitation token" in response.json()["detail"]

@pytest.mark.asyncio
async def test_register_duplicate_phone(client: AsyncClient, test_db):
    """Test registration with a phone number that's already registered."""
    # Create a test invitation
    invitation = Invitation(
        email="new@example.com",
        token="another_valid_token",
        status=InvitationStatus.PENDING,
        expires_at=datetime.utcnow() + timedelta(days=1)
    )
    
    # Create an existing user with the same phone number
    existing_user = User(
        full_name="Existing User",
        email="existing@example.com",
        password_hash="hashed_password",
        phone_number="+254712345678"
    )
    
    test_db.add(invitation)
    test_db.add(existing_user)
    await test_db.commit()
    
    # Make the request
    response = await client.post(
        "/api/v1/auth/register?invitation_token=another_valid_token",
        json={
            "full_name": "New User",
            "password": "password123",
            "phone_number": "+254712345678"  # Same as existing user
        }
    )
    
    assert response.status_code == 409
    assert "Phone number is already registered" in response.json()["detail"]

@pytest.mark.asyncio
async def test_register_invalid_phone_format(client: AsyncClient, test_db):
    """Test registration with an invalid phone number format."""
    # Create a test invitation
    invitation = Invitation(
        email="test@example.com",
        token="phone_format_test_token",
        status=InvitationStatus.PENDING,
        expires_at=datetime.utcnow() + timedelta(days=1)
    )
    test_db.add(invitation)
    await test_db.commit()
    
    # Make the request with invalid phone format
    response = await client.post(
        "/api/v1/auth/register?invitation_token=phone_format_test_token",
        json={
            "full_name": "Test User",
            "password": "password123",
            "phone_number": "0712345678"  # Missing +254 prefix
        }
    )
    
    assert response.status_code == 422
    assert "Phone number must be in valid Kenyan format" in response.json()["detail"][0]["msg"]

@pytest.mark.asyncio
async def test_register_expired_token(client: AsyncClient, test_db):
    """Test registration with an expired token."""
    # Create an expired invitation
    expired_invitation = Invitation(
        email="expired@example.com",
        token="expired_test_token",
        status=InvitationStatus.PENDING,
        expires_at=datetime.utcnow() - timedelta(days=1) # Expired yesterday
    )
    test_db.add(expired_invitation)
    await test_db.commit()

    response = await client.post(
        "/api/v1/auth/register?invitation_token=expired_test_token",
        json={
            "full_name": "Test User",
            "password": "password123",
            "phone_number": "+254700000000"
        }
    )

    assert response.status_code == 404
    assert "Invalid or expired invitation token" in response.json()["detail"]

@pytest.mark.asyncio
async def test_register_used_token(client: AsyncClient, test_db):
    """Test registration with an already used (accepted) token."""
    # Create a used invitation
    used_invitation = Invitation(
        email="used@example.com",
        token="used_test_token",
        status=InvitationStatus.ACCEPTED, # Already accepted
        expires_at=datetime.utcnow() + timedelta(days=1) # Not expired
    )
    test_db.add(used_invitation)
    await test_db.commit()

    response = await client.post(
        "/api/v1/auth/register?invitation_token=used_test_token",
        json={
            "full_name": "Test User",
            "password": "password123",
            "phone_number": "+254711111111"
        }
    )

    assert response.status_code == 404
    assert "Invalid or expired invitation token" in response.json()["detail"]