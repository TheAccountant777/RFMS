import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth_service import AuthService
from app.models.invitation import Invitation, InvitationStatus
from app.models.user import User
from app.models.referral_link import ReferralLink
from app.schemas.user import UserCreate
from app.exceptions import NotFoundError, ConflictError

@pytest.fixture
def mock_db():
    """Create a mock database session."""
    db = AsyncMock(spec=AsyncSession)
    return db

@pytest.fixture
def valid_invitation():
    """Create a valid invitation object."""
    return Invitation(
        id="123e4567-e89b-12d3-a456-426614174000",
        email="test@example.com",
        token="valid_token",
        status=InvitationStatus.PENDING,
        expires_at=datetime.utcnow() + timedelta(days=1)
    )

@pytest.fixture
def valid_user_data():
    """Create valid user registration data."""
    return UserCreate(
        full_name="Test User",
        password="password123",
        phone_number="+254712345678",
        email="test@example.com"  # This will be overridden by the invitation email
    )

@pytest.mark.asyncio
async def test_register_participant_success(mock_db, valid_invitation, valid_user_data):
    """Test successful participant registration."""
    # Setup mocks for the execute calls
    execute_mock = AsyncMock()
    
    # First call for invitation lookup
    first_result_mock = AsyncMock()
    first_result_mock.scalar_one_or_none.return_value = valid_invitation
    
    # Second call for existing phone number check
    second_result_mock = AsyncMock()
    second_result_mock.scalar_one_or_none.return_value = None
    
    # Third call for unique code check
    third_result_mock = AsyncMock()
    third_result_mock.scalar_one_or_none.return_value = None
    
    # Set up the side effect for execute
    execute_mock.side_effect = [first_result_mock, second_result_mock, third_result_mock]
    mock_db.execute = execute_mock
    
    # Mock the User object that will be created
    mock_user = MagicMock(spec=User)
    mock_user.id = "123e4567-e89b-12d3-a456-426614174001"
    
    # Mock the flush to simulate setting the user ID
    mock_db.flush = AsyncMock()
    
    # Mock the commit and refresh methods
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    
    # Patch the security functions
    with patch('app.services.auth_service.hash_password', return_value="hashed_password"), \
         patch('app.services.auth_service.create_access_token', return_value="access_token"), \
         patch('app.services.auth_service.create_refresh_token', return_value="refresh_token"), \
         patch('app.services.auth_service.generate_unique_code', return_value="ABCDEFGH"):
        
        # Call the method under test
        auth_service = AuthService(mock_db)
        result = await auth_service.register_participant("valid_token", valid_user_data)
        
        # Assertions
        assert result.access_token == "access_token"
        assert result.refresh_token == "refresh_token"
        
        # Verify database interactions
        assert mock_db.add.call_count == 2  # User and ReferralLink
        assert mock_db.execute.call_count == 3  # Invitation lookup, phone check, and update invitation
        assert mock_db.commit.call_count == 1
        assert mock_db.refresh.call_count == 1

@pytest.mark.asyncio
async def test_register_participant_invalid_token(mock_db, valid_user_data):
    """Test registration with invalid token."""
    # Setup mock to return None for invitation lookup
    result_mock = AsyncMock()
    result_mock.scalar_one_or_none.return_value = None
    
    execute_mock = AsyncMock()
    execute_mock.return_value = result_mock
    mock_db.execute = execute_mock
    
    # Call the method under test
    auth_service = AuthService(mock_db)
    
    # Assert that it raises NotFoundError
    with pytest.raises(NotFoundError):
        await auth_service.register_participant("invalid_token", valid_user_data)

@pytest.mark.asyncio
async def test_register_participant_duplicate_phone(mock_db, valid_invitation, valid_user_data):
    """Test registration with a phone number that's already registered."""
    # Setup mocks for the execute calls
    execute_mock = AsyncMock()
    
    # First call for invitation lookup
    first_result_mock = AsyncMock()
    first_result_mock.scalar_one_or_none.return_value = valid_invitation
    
    # Second call for existing phone number check - return a user to simulate duplicate
    second_result_mock = AsyncMock()
    second_result_mock.scalar_one_or_none.return_value = User()
    
    # Set up the side effect for execute
    execute_mock.side_effect = [first_result_mock, second_result_mock]
    mock_db.execute = execute_mock
    
    # Call the method under test
    auth_service = AuthService(mock_db)
    
    # Assert that it raises ConflictError
    with pytest.raises(ConflictError):
        await auth_service.register_participant("valid_token", valid_user_data)