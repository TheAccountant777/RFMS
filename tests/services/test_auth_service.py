import pytest
from unittest.mock import AsyncMock, MagicMock, patch # Import patch from unittest.mock
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.services.auth_service import AuthService
from app.models.invitation import Invitation, InvitationStatus # Import InvitationStatus
from app.exceptions import ConflictError
from app.services.email_service import EmailService # Import the actual class for mocking

# Mock the email_service instance globally
email_service_mock = AsyncMock(spec=EmailService)
# Patch the imported email_service instance in the auth_service module
pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_db_session():
    """Fixture to provide a mock AsyncSession."""
    session = AsyncMock(spec=AsyncSession)
    # Mock the execute method to return a mock result with scalar_one_or_none
    session.execute.return_value = MagicMock()
    session.execute.return_value.scalar_one_or_none.return_value = None # Default: no existing invitation
    return session

@pytest.fixture
def auth_service(mock_db_session: AsyncMock):
    """Fixture to provide an AuthService instance with a mock session."""
    # Temporarily patch the email_service instance used within AuthService
    original_email_service = AuthService.__module__ + '.email_service'
    with patch(original_email_service, email_service_mock): # Use patch from unittest.mock
        service = AuthService(mock_db_session)
        yield service
    # Reset the mock after the test
    email_service_mock.reset_mock()


async def test_create_invitation_success(auth_service: AuthService, mock_db_session: AsyncMock):
    """Test successful invitation creation and email sending."""
    email = "new.user@example.com"

    # Mock the database add and refresh operations
    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.return_value = None

    # Mock the return value of the select query to indicate no existing invitation
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None

    invitation = await auth_service.create_invitation(email)

    # Assert that a new invitation object was added to the session
    mock_db_session.add.assert_called_once()
    added_invitation = mock_db_session.add.call_args[0][0]
    assert isinstance(added_invitation, Invitation)
    assert added_invitation.email == email
    assert added_invitation.status == InvitationStatus.PENDING # Assert against the Enum member
    assert added_invitation.token is not None
    assert added_invitation.expires_at > datetime.utcnow()

    # Assert that the session was committed and refreshed
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(added_invitation)

    # Assert that the email service was called with the correct parameters
    email_service_mock.send_invitation_email.assert_called_once_with(email, added_invitation.token)

    # Assert the returned object is the database invitation object
    assert invitation == added_invitation


async def test_create_invitation_conflict(auth_service: AuthService, mock_db_session: AsyncMock):
    """Test creating an invitation for an email with an existing pending invitation."""
    email = "existing.user@example.com"

    # Mock the database query to return an existing invitation
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = Invitation(email=email, token="fake_token", status=InvitationStatus.PENDING, expires_at=datetime.utcnow() + timedelta(days=1)) # Use Enum member

    # Assert that a ConflictError is raised
    with pytest.raises(ConflictError, match=f"An active invitation already exists for {email}"):
        await auth_service.create_invitation(email)

    # Assert that no database changes were made
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_called()
    mock_db_session.refresh.assert_not_called()

    # Assert that the email service was not called
    email_service_mock.send_invitation_email.assert_not_called()