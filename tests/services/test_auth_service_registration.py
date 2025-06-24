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
    
    # Mock results for various execute calls
    invitation_lookup_result = AsyncMock()
    invitation_lookup_result.scalar_one_or_none.return_value = valid_invitation
    
    phone_check_result = AsyncMock()
    phone_check_result.scalar_one_or_none.return_value = None # No existing user with this phone
    
    unique_code_check_result = AsyncMock()
    unique_code_check_result.scalar_one_or_none.return_value = None # Generated unique code is unique
    
    # For the update statement, execute doesn't return a scalar
    update_invitation_result = AsyncMock()

    # Set up the side effect for execute
    # Order: 1. Find Invitation, 2. Check Phone, 3. Check Unique Code, 4. Update Invitation
    execute_mock.side_effect = [
        invitation_lookup_result,
        phone_check_result,
        unique_code_check_result,
        update_invitation_result
    ]
    mock_db.execute = execute_mock
    
    # Mock the User object that will be created and added to session
    # We need to know its ID for token generation assertion
    # The actual User object is created inside the service method.
    # We can capture what's added to db.add
    
    # Mock the flush to simulate setting the user ID
    # When new_user is added and flush is called, it should get an ID.
    # We'll have User and ReferralLink added.
    # Let's assume the User object is the first one added.
    async def flush_effect(*args, **kwargs):
        # Simulate that the first object added (User) gets an ID
        # This is a simplification; real flush assigns IDs to all unflushed objects
        if mock_db.add.call_args_list:
            first_added_obj = mock_db.add.call_args_list[0].args[0]
            if isinstance(first_added_obj, User):
                first_added_obj.id = "mock_user_id_value"

    mock_db.flush = AsyncMock(side_effect=flush_effect)
    
    # Mock the commit and refresh methods
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    
    # Patch the security functions
    with patch('app.services.auth_service.hash_password', return_value="hashed_password"), \
         patch('app.services.auth_service.create_access_token', return_value="access_token"), \
         patch('app.services.auth_service.create_refresh_token', return_value="refresh_token"), \
         patch('app.services.auth_service.generate_unique_code', return_value="ABCDEFGH") as mock_generate_code:
        
        # Call the method under test
        auth_service = AuthService(mock_db)
        result = await auth_service.register_participant("valid_token", valid_user_data)
        
        # Assertions on returned tokens
        assert result.access_token == "access_token"
        assert result.refresh_token == "refresh_token"

        # Assertions on patched functions
        mock_hash_password.assert_called_once_with(valid_user_data.password)
        mock_create_access_token.assert_called_once_with(data={"sub": "mock_user_id_value"})
        mock_create_refresh_token.assert_called_once_with(data={"sub": "mock_user_id_value"})
        mock_generate_code.assert_called_once()

        # Verify database interactions
        assert mock_db.add.call_count == 2  # User and ReferralLink
        added_objects = [call.args[0] for call in mock_db.add.call_args_list]

        user_added = next(obj for obj in added_objects if isinstance(obj, User))
        referral_link_added = next(obj for obj in added_objects if isinstance(obj, ReferralLink))

        assert user_added.full_name == valid_user_data.full_name
        assert user_added.email == valid_invitation.email # Email from invitation
        assert user_added.password_hash == "hashed_password"
        assert user_added.phone_number == valid_user_data.phone_number

        assert referral_link_added.user_id == "mock_user_id_value"
        assert referral_link_added.unique_code == "ABCDEFGH"

        assert mock_db.execute.call_count == 4
        # Check the update call for invitation
        update_call_args = mock_db.execute.call_args_list[3].args[0] # 4th call
        assert str(update_call_args.compile(compile_kwargs={"literal_binds": True})).startswith(
            "UPDATE invitations SET status='ACCEPTED' WHERE invitations.id ="
        )
        # Note: Checking the exact ID in the update requires knowing valid_invitation.id
        # assert valid_invitation.id in str(update_call_args) # This is tricky due to UUID vs str

        assert mock_db.commit.call_count == 1
        assert mock_db.refresh.call_count == 1 # Called with new_user

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

@pytest.mark.asyncio
async def test_register_participant_expired_token(mock_db, valid_user_data):
    """Test registration with an expired token."""
    expired_invitation = Invitation(
        id="123e4567-e89b-12d3-a456-426614174002",
        email="expired@example.com",
        token="expired_token",
        status=InvitationStatus.PENDING, # Status is pending
        expires_at=datetime.utcnow() - timedelta(days=1) # But expired
    )

    result_mock = AsyncMock()
    result_mock.scalar_one_or_none.return_value = None # Service query will find nothing due to expiry

    execute_mock = AsyncMock(return_value=result_mock)
    mock_db.execute = execute_mock

    auth_service = AuthService(mock_db)
    with pytest.raises(NotFoundError) as excinfo:
        await auth_service.register_participant("expired_token", valid_user_data)
    assert "Invalid or expired invitation token" in str(excinfo.value)

    # Ensure the query for invitation was actually made
    # The service logic is `Invitation.token == invitation_token, Invitation.status == InvitationStatus.PENDING, Invitation.expires_at > datetime.utcnow()`
    # So, if the mock scalar_one_or_none.return_value is None, the test passes.
    # To be more rigorous, we could mock scalar_one_or_none to return expired_invitation
    # and assert that the service's internal logic correctly deems it invalid.
    # However, the current service logic directly filters by expires_at in the query.
    # So, scalar_one_or_none() returning None is the correct outcome of that query.
    mock_db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_register_participant_used_token(mock_db, valid_user_data):
    """Test registration with an already used (ACCEPTED) token."""
    used_invitation = Invitation(
        id="123e4567-e89b-12d3-a456-426614174003",
        email="used@example.com",
        token="used_token",
        status=InvitationStatus.ACCEPTED, # Status is ACCEPTED
        expires_at=datetime.utcnow() + timedelta(days=1) # Not expired
    )

    result_mock = AsyncMock()
    result_mock.scalar_one_or_none.return_value = None # Service query will find nothing due to status

    execute_mock = AsyncMock(return_value=result_mock)
    mock_db.execute = execute_mock

    auth_service = AuthService(mock_db)
    with pytest.raises(NotFoundError) as excinfo:
        await auth_service.register_participant("used_token", valid_user_data)
    assert "Invalid or expired invitation token" in str(excinfo.value)

    # Similar to the expired token test, the service query filters by status=PENDING.
    # So, scalar_one_or_none() returning None is the correct outcome.
    mock_db.execute.assert_called_once()