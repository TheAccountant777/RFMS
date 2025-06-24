import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta
import uuid

from app.models.invitation import Invitation, InvitationStatus
from app.models.admin_user import AdminUser
from app.core.security import create_access_token
from app.dependencies import get_current_admin_user
from app.services.email_service import EmailService

# Mock the email_service instance globally for integration tests
email_service_mock = AsyncMock(spec=EmailService)

# Temporarily patch the email_service instance used within AuthService
original_email_service_path = 'app.services.auth_service.email_service'
pytestmark = pytest.mark.asyncio

@pytest.fixture(autouse=True)
def mock_email_service_in_auth_service():
    """Fixture to patch the email_service instance within the AuthService module."""
    with patch(original_email_service_path, email_service_mock):
        yield
    # Reset the mock after each test
    email_service_mock.reset_mock()

@pytest.fixture(autouse=True)
def override_admin_dependency(client, async_session):
    """Override the admin user dependency for testing."""
    from app.main import app
    from app.dependencies import get_db
    
    def override_get_current_admin_user():
        """Overrides the admin user dependency to return a mock admin user."""
        return {"email": "testadmin@example.com", "role": "CTO"}
    
    async def override_get_db():
        """Override database dependency to use test database."""
        yield async_session
    
    app.dependency_overrides[get_current_admin_user] = override_get_current_admin_user
    app.dependency_overrides[get_db] = override_get_db
    yield
    # Clean up after test
    if get_current_admin_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_admin_user]
    if get_db in app.dependency_overrides:
        del app.dependency_overrides[get_db]


async def test_create_invitation_success(client: AsyncClient, async_session: AsyncSession):
    """Test successful creation of an invitation via the API."""
    email = "new.participant@example.com"

    response = await client.post("/api/v1/admin/invitations/", params={"email": email})

    if response.status_code != 201:
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
    
    assert response.status_code == 201
    data = response.json()

    assert data["email"] == email
    assert data["status"] == "PENDING"
    assert "id" in data
    assert "token" in data
    assert "expires_at" in data
    assert "created_at" in data

    # Verify the invitation was created in the database
    invitation_in_db = await async_session.execute(
        select(Invitation).where(Invitation.email == email)
    )
    invitation = invitation_in_db.scalar_one_or_none()
    assert invitation is not None
    assert invitation.email == email
    assert invitation.status == InvitationStatus.PENDING
    assert invitation.token is not None
    assert invitation.expires_at > datetime.utcnow() - timedelta(minutes=1)

    # Verify email service was called
    email_service_mock.send_invitation_email.assert_called_once_with(email, invitation.token)


async def test_create_invitation_conflict(client: AsyncClient, async_session: AsyncSession):
    """Test attempting to create an invitation for an email with an existing pending invitation."""
    email = "existing.pending@example.com"

    # Pre-seed an existing pending invitation
    existing_invitation = Invitation(
        id=uuid.uuid4(),
        email=email,
        token="existing_token",
        status=InvitationStatus.PENDING,
        expires_at=datetime.utcnow() + timedelta(days=1),
        created_at=datetime.utcnow()
    )
    async_session.add(existing_invitation)
    await async_session.commit()

    response = await client.post("/api/v1/admin/invitations/", params={"email": email})

    assert response.status_code == 409
    data = response.json()
    assert "detail" in data
    assert f"An active invitation already exists for {email}" in data["detail"]

    # Verify no new invitation was created in the database
    invitations_in_db = await async_session.execute(
        select(Invitation).where(Invitation.email == email)
    )
    # Should still only have the one existing invitation
    assert len(invitations_in_db.scalars().all()) == 1

    # Verify email service was not called
    email_service_mock.send_invitation_email.assert_not_called()