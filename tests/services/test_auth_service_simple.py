import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from app.services.auth_service import AuthService
from app.models.invitation import Invitation, InvitationStatus
from app.models.user import User
from app.schemas.user import UserCreate
from app.schemas.auth import JWTTokens
from app.exceptions import NotFoundError, ConflictError

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
async def test_register_participant_success(mocker, valid_user_data):
    """Test successful participant registration."""
    # Create mock objects
    mock_db = mocker.Mock()
    
    # Create a valid invitation
    valid_invitation = Invitation(
        id="123e4567-e89b-12d3-a456-426614174000",
        email="test@example.com",
        token="valid_token",
        status=InvitationStatus.PENDING,
        expires_at=datetime.utcnow() + timedelta(days=1)
    )
    
    # Setup the first query to return the invitation
    first_result = mocker.Mock()
    first_result.scalar_one_or_none.return_value = valid_invitation
    
    # Setup the second query to return None (no duplicate phone)
    second_result = mocker.Mock()
    second_result.scalar_one_or_none.return_value = None
    
    # Setup the third query to return None (no duplicate code)
    third_result = mocker.Mock()
    third_result.scalar_one_or_none.return_value = None
    
    # Setup the fourth query (update invitation status)
    fourth_result = mocker.Mock()
    
    # Configure the execute method to return different results for different calls
    mock_db.execute = mocker.AsyncMock()
    mock_db.execute.side_effect = [first_result, second_result, third_result, fourth_result]
    
    # Mock other database methods
    mock_db.flush = mocker.AsyncMock()
    mock_db.commit = mocker.AsyncMock()
    mock_db.refresh = mocker.AsyncMock()
    
    # Create a mock user with an ID
    mock_user = mocker.Mock()
    mock_user.id = "123e4567-e89b-12d3-a456-426614174001"
    
    # Patch the necessary functions and classes
    with patch('app.services.auth_service.select', mocker.Mock()), \
         patch('app.services.auth_service.update', mocker.Mock()), \
         patch('app.services.auth_service.User', return_value=mock_user), \
         patch('app.services.auth_service.ReferralLink', mocker.Mock()), \
         patch('app.services.auth_service.hash_password', return_value="hashed_password"), \
         patch('app.services.auth_service.create_access_token', return_value="access_token"), \
         patch('app.services.auth_service.create_refresh_token', return_value="refresh_token"), \
         patch('app.services.auth_service.generate_unique_code', return_value="ABCDEFGH"):
        
        # Create the service with the mock DB
        auth_service = AuthService(mock_db)
        
        # Call the method
        result = await auth_service.register_participant("valid_token", valid_user_data)
        
        # Verify the result
        assert isinstance(result, JWTTokens)
        assert result.access_token == "access_token"
        assert result.refresh_token == "refresh_token"
        
        # Verify database interactions
        assert mock_db.add.call_count == 2  # User and ReferralLink
        assert mock_db.execute.call_count == 4  # Invitation lookup, phone check, unique code check, and update invitation
        assert mock_db.commit.call_count == 1
        assert mock_db.refresh.call_count == 1

@pytest.mark.asyncio
async def test_register_participant_invalid_token(mocker, valid_user_data):
    """Test registration with an invalid token."""
    # Create mock objects
    mock_db = mocker.Mock()
    
    # Setup the first query to return None (invalid token)
    first_result = mocker.Mock()
    first_result.scalar_one_or_none.return_value = None
    
    # Configure the execute method
    mock_db.execute = mocker.AsyncMock()
    mock_db.execute.return_value = first_result
    
    # Patch the select function
    with patch('app.services.auth_service.select', mocker.Mock()):
        # Create the service with the mock DB
        auth_service = AuthService(mock_db)
        
        # Test that it raises NotFoundError
        with pytest.raises(NotFoundError):
            await auth_service.register_participant("invalid_token", valid_user_data)

@pytest.mark.asyncio
async def test_register_participant_duplicate_phone(mocker, valid_user_data):
    """Test registration with a phone number that's already registered."""
    # Create mock objects
    mock_db = mocker.Mock()
    
    # Create a valid invitation
    valid_invitation = Invitation(
        id="123e4567-e89b-12d3-a456-426614174000",
        email="test@example.com",
        token="valid_token",
        status=InvitationStatus.PENDING,
        expires_at=datetime.utcnow() + timedelta(days=1)
    )
    
    # Setup the first query to return the invitation
    first_result = mocker.Mock()
    first_result.scalar_one_or_none.return_value = valid_invitation
    
    # Setup the second query to return a user (indicating duplicate phone)
    second_result = mocker.Mock()
    second_result.scalar_one_or_none.return_value = User()
    
    # Configure the execute method to return different results for different calls
    mock_db.execute = mocker.AsyncMock()
    mock_db.execute.side_effect = [first_result, second_result]
    
    # Patch the select function
    with patch('app.services.auth_service.select', mocker.Mock()):
        # Create the service with the mock DB
        auth_service = AuthService(mock_db)
        
        # Test that it raises ConflictError
        with pytest.raises(ConflictError):
            await auth_service.register_participant("valid_token", valid_user_data)