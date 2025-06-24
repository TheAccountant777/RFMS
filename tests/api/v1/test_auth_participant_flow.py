import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.admin_user import AdminUser
from app.core.security import hash_password # For creating test users
import uuid

# Assume conftest.py provides fixtures for:
# - async_client: The FastAPI TestClient wrapped for async.
# - db_session: The SQLAlchemy AsyncSession for database interactions.
# - test_user_factory: A factory to create users.
# - test_admin_user_factory: A factory to create admin users.
# - logged_in_test_participant: A fixture that creates a participant and returns tokens.
# - logged_in_test_admin: A fixture that creates an admin and returns tokens.

pytestmark = pytest.mark.asyncio

# Helper to get tokens by logging in (assuming /auth/login is implemented)
# This might be better as a fixture in conftest.py
async def login_user_for_tokens(async_client: AsyncClient, email: str, password: str) -> dict:
    response = await async_client.post("/api/v1/auth/login", data={"username": email, "password": password})
    response.raise_for_status() # Ensure login was successful
    return response.json()


@pytest.fixture(scope="function")
async def test_participant(db_session: AsyncSession):
    from app.models.user import User, UserStatus # Assuming UserStatus enum

    participant_email = f"participant_{uuid.uuid4()}@example.com"
    participant_password = "testpassword123"

    user = User(
        email=participant_email,
        full_name="Test Participant User",
        phone_number=f"+2547{str(uuid.uuid4().int)[:8]}", # Random phone
        password_hash=hash_password(participant_password),
        status=UserStatus.ACTIVE
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return {"email": participant_email, "password": participant_password, "id": user.id}

@pytest.fixture(scope="function")
async def test_admin(db_session: AsyncSession):
    from app.models.admin_user import AdminUser, AdminRole # Assuming AdminRole enum

    admin_email = f"admin_{uuid.uuid4()}@example.com"
    admin_password = "testadminpassword123"

    admin = AdminUser(
        email=admin_email,
        password_hash=hash_password(admin_password),
        role=AdminRole.FINANCE # Or any role
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return {"email": admin_email, "password": admin_password, "id": admin.id}


async def test_full_auth_participant_flow(async_client: AsyncClient, test_participant):
    # 1. Login test participant
    login_payload = {"username": test_participant['email'], "password": test_participant['password']}
    response = await async_client.post("/api/v1/auth/login", data=login_payload)
    assert response.status_code == 200, response.text
    tokens = response.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    # 2. Call /api/v1/participant/me with the access token
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await async_client.get("/api/v1/participant/me", headers=headers)
    assert response.status_code == 200, response.text
    profile = response.json()
    assert profile["email"] == test_participant["email"]
    assert profile["id"] == str(test_participant["id"])
    assert "full_name" in profile
    assert "phone_number" in profile

    # 3. Call /api/v1/auth/refresh with the refresh token
    response = await async_client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200, response.text
    new_tokens = response.json()
    new_access_token = new_tokens["access_token"]
    assert "refresh_token" not in new_tokens or new_tokens["refresh_token"] is None # As per plan

    # 4. Call /api/v1/participant/me with the *new* access token
    headers = {"Authorization": f"Bearer {new_access_token}"}
    response = await async_client.get("/api/v1/participant/me", headers=headers)
    assert response.status_code == 200, response.text
    profile = response.json()
    assert profile["email"] == test_participant["email"]

async def test_refresh_with_invalid_token(async_client: AsyncClient):
    response = await async_client.post("/api/v1/auth/refresh", json={"refresh_token": "invalid.refresh.token"})
    assert response.status_code == 401, response.text
    assert "Could not validate credentials" in response.json()["detail"] # Or specific error for bad token

async def test_refresh_with_access_token_as_refresh_token(async_client: AsyncClient, test_participant):
    # Login to get a valid access token
    login_payload = {"username": test_participant['email'], "password": test_participant['password']}
    response = await async_client.post("/api/v1/auth/login", data=login_payload)
    assert response.status_code == 200
    tokens = response.json()
    access_token = tokens["access_token"]

    # Attempt to use the access token as a refresh token
    response = await async_client.post("/api/v1/auth/refresh", json={"refresh_token": access_token})
    assert response.status_code == 401, response.text # Expecting 401 due to wrong token type
    assert "Invalid token type, expected refresh token" in response.json()["detail"]


async def test_access_me_unauthenticated(async_client: AsyncClient):
    response = await async_client.get("/api/v1/participant/me")
    assert response.status_code == 401, response.text # FastAPI default for missing token
    # Detail might vary, could be "Not authenticated" or similar

async def test_access_me_with_invalid_token(async_client: AsyncClient):
    headers = {"Authorization": "Bearer invalid.access.token"}
    response = await async_client.get("/api/v1/participant/me", headers=headers)
    assert response.status_code == 401, response.text
    # Detail from get_current_user's token validation

async def test_access_me_with_admin_token_forbidden(async_client: AsyncClient, test_admin):
    # 1. Login test admin
    login_payload = {"username": test_admin['email'], "password": test_admin['password']}
    response = await async_client.post("/api/v1/auth/login", data=login_payload)
    assert response.status_code == 200, response.text
    tokens = response.json()
    admin_access_token = tokens["access_token"]

    # 2. Attempt to call /api/v1/participant/me with admin's access token
    headers = {"Authorization": f"Bearer {admin_access_token}"}
    response = await async_client.get("/api/v1/participant/me", headers=headers)
    assert response.status_code == 403, response.text
    assert "Access forbidden: Participant role required" in response.json()["detail"]

# Note: This test file assumes that the /api/v1/auth/login endpoint is functional
# and returns tokens in the format {"access_token": "...", "refresh_token": "..."}.
# It also assumes UserStatus and AdminRole enums are available in their respective models.
# The login endpoint for FastAPI's OAuth2PasswordRequestForm expects 'username' and 'password' fields.
# The test users are created directly in the DB for simplicity in these fixtures.
# A more robust setup might use a user factory or service calls if available.
# The `db_session` fixture is assumed to handle transaction cleanup.
# `async_client` is assumed to be the TestClient from FastAPI, correctly configured.
# Ensure `UserStatus` and `AdminRole` are importable/defined in models.
# E.g. app/models/user.py:
# import enum
# class UserStatus(str, enum.Enum):
#    ACTIVE = "ACTIVE"
#    INACTIVE = "INACTIVE"

# E.g. app/models/admin_user.py:
# import enum
# class AdminRole(str, enum.Enum):
#    CTO = "CTO"
#    CEO = "CEO"
#    FINANCE = "FINANCE"
#    # ... other roles
