import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid_extensions import uuid7 # Using uuid7 as per existing tests for ID generation
from fastapi import HTTPException

from app.services.auth_service import AuthService
from app.models.user import User
from app.models.admin_user import AdminUser
from app.schemas.auth import JWTTokens
from app.core.security import verify_password, create_access_token, create_refresh_token

@pytest.fixture
def mock_db_session():
    return AsyncMock()

@pytest.fixture
def auth_service(mock_db_session):
    return AuthService(mock_db_session)

@pytest.mark.asyncio
async def test_login_user_participant_success(auth_service, mock_db_session):
    mock_user_id = uuid.uuid4() # Changed to uuid.uuid4()
    mock_user = User(id=mock_user_id, email="participant@example.com", password_hash="hashed_password")

    # Mock DB response for User
    mock_result_user = MagicMock()
    mock_result_user.scalar_one_or_none.return_value = mock_user

    # First execute call for User, second for AdminUser (will return None)
    mock_db_session.execute.side_effect = [mock_result_user, MagicMock(scalar_one_or_none=MagicMock(return_value=None))]

    with patch("app.services.auth_service.verify_password", return_value=True) as mock_verify_password, \
         patch("app.services.auth_service.create_access_token", return_value="access_token_str") as mock_create_access, \
         patch("app.services.auth_service.create_refresh_token", return_value="refresh_token_str") as mock_create_refresh:

        tokens = await auth_service.login_user(email="participant@example.com", password="password123")

        mock_db_session.execute.assert_any_call(pytest.ANY) # Check User query
        # The second call for AdminUser might not happen if User is found and password verified first in some logic,
        # but current logic checks User then AdminUser if first is None.
        # For this successful participant case, only the first execute matters for finding the user.

        mock_verify_password.assert_called_once_with("password123", "hashed_password")
        mock_create_access.assert_called_once_with(data={"sub": str(mock_user_id), "user_type": "user"})
        mock_create_refresh.assert_called_once_with(data={"sub": str(mock_user_id), "user_type": "user"})

        assert isinstance(tokens, JWTTokens)
        assert tokens.access_token == "access_token_str"
        assert tokens.refresh_token == "refresh_token_str"
        assert tokens.token_type == "bearer"

@pytest.mark.asyncio
async def test_login_admin_success(auth_service, mock_db_session):
    mock_admin_id = uuid.uuid4() # Changed to uuid.uuid4()
    mock_admin = AdminUser(id=mock_admin_id, email="admin@example.com", password_hash="hashed_admin_password", role="CEO")

    # Mock DB response: User not found, then AdminUser found
    mock_result_user_none = MagicMock()
    mock_result_user_none.scalar_one_or_none.return_value = None # User not found
    mock_result_admin_found = MagicMock()
    mock_result_admin_found.scalar_one_or_none.return_value = mock_admin # Admin found

    mock_db_session.execute.side_effect = [mock_result_user_none, mock_result_admin_found]

    with patch("app.services.auth_service.verify_password", return_value=True) as mock_verify_password, \
         patch("app.services.auth_service.create_access_token", return_value="admin_access_token") as mock_create_access, \
         patch("app.services.auth_service.create_refresh_token", return_value="admin_refresh_token") as mock_create_refresh:

        tokens = await auth_service.login_user(email="admin@example.com", password="adminpassword")

        assert mock_db_session.execute.call_count == 2 # Called for User then AdminUser
        mock_verify_password.assert_called_once_with("adminpassword", "hashed_admin_password")
        mock_create_access.assert_called_once_with(data={"sub": str(mock_admin_id), "user_type": "adminuser"})
        mock_create_refresh.assert_called_once_with(data={"sub": str(mock_admin_id), "user_type": "adminuser"})

        assert isinstance(tokens, JWTTokens)
        assert tokens.access_token == "admin_access_token"
        assert tokens.refresh_token == "admin_refresh_token"

@pytest.mark.asyncio
async def test_login_user_wrong_password(auth_service, mock_db_session):
    mock_user_id = uuid.uuid4() # Changed to uuid.uuid4()
    mock_user = User(id=mock_user_id, email="participant@example.com", password_hash="hashed_password")

    mock_result_user = MagicMock()
    mock_result_user.scalar_one_or_none.return_value = mock_user
    mock_db_session.execute.return_value = mock_result_user # Only one call needed if user is found

    with patch("app.services.auth_service.verify_password", return_value=False) as mock_verify_password:
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.login_user(email="participant@example.com", password="wrongpassword")

        mock_verify_password.assert_called_once_with("wrongpassword", "hashed_password")
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid email or password"

@pytest.mark.asyncio
async def test_login_admin_wrong_password(auth_service, mock_db_session):
    mock_admin_id = uuid.uuid4() # Changed to uuid.uuid4()
    mock_admin = AdminUser(id=mock_admin_id, email="admin@example.com", password_hash="hashed_admin_password", role="CEO")

    mock_result_user_none = MagicMock()
    mock_result_user_none.scalar_one_or_none.return_value = None
    mock_result_admin_found = MagicMock()
    mock_result_admin_found.scalar_one_or_none.return_value = mock_admin

    mock_db_session.execute.side_effect = [mock_result_user_none, mock_result_admin_found]

    with patch("app.services.auth_service.verify_password", return_value=False) as mock_verify_password:
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.login_user(email="admin@example.com", password="wrongpassword")

        mock_verify_password.assert_called_once_with("wrongpassword", "hashed_admin_password")
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid email or password"

@pytest.mark.asyncio
async def test_login_email_not_found(auth_service, mock_db_session):
    # Mock DB to return None for both User and AdminUser lookups
    mock_result_none = MagicMock()
    mock_result_none.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_result_none # Both calls will use this

    with patch("app.services.auth_service.verify_password") as mock_verify_password: # Should not be called
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.login_user(email="nonexistent@example.com", password="password123")

        assert mock_db_session.execute.call_count == 2 # Checked User then AdminUser
        mock_verify_password.assert_not_called()
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid email or password"

# Basic test to ensure User and AdminUser models can be instantiated for tests
def test_user_model_instantiation():
    user_id = uuid.uuid4() # Changed to uuid.uuid4()
    user = User(id=user_id, full_name="Test User", email="test@example.com", password_hash="hash", phone_number="+254712345678")
    assert user.email == "test@example.com"

def test_admin_model_instantiation():
    admin_id = uuid.uuid4() # Changed to uuid.uuid4()
    admin = AdminUser(id=admin_id, email="admin@example.com", password_hash="hash", role="CEO")
    assert admin.email == "admin@example.com"

# Ensure direct import works for patching if needed, though usually patch by string path
def test_security_functions_exist():
    assert callable(verify_password)
    assert callable(create_access_token)
    assert callable(create_refresh_token)

# Placeholder for potential setup/teardown if tests grow more complex
def setup_function():
    pass

def teardown_function():
    pass
