import pytest
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserStatus
from app.models.admin_user import AdminUser, AdminRole
from app.core.security import hash_password
from app.config import settings # For base API path if needed, though usually client handles it

# Assume a TestClient-like fixture `client` is provided by conftest.py
# Assume an AsyncSession fixture `db_session` is provided for database operations

@pytest.mark.asyncio
async def test_login_participant_success(client: httpx.AsyncClient, db_session: AsyncSession):
    # 1. Setup: Create a participant user in the test database
    plain_password = "participant_password123"
    hashed_pw = hash_password(plain_password)
    participant = User(
        full_name="Test Participant Login",
        email="participant.login@example.com",
        password_hash=hashed_pw,
        phone_number="+254712345001", # Unique phone number
        status=UserStatus.ACTIVE
    )
    db_session.add(participant)
    await db_session.commit()
    await db_session.refresh(participant)

    # 2. Action: Make login request
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "participant.login@example.com", "password": plain_password}
    )

    # 3. Assert: Correct response
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    # Cleanup: User will be removed by transaction rollback or test DB teardown
    await db_session.delete(participant)
    await db_session.commit()


@pytest.mark.asyncio
async def test_login_admin_success(client: httpx.AsyncClient, db_session: AsyncSession):
    # 1. Setup: Create an admin user
    plain_password = "admin_password123"
    hashed_pw = hash_password(plain_password)
    admin = AdminUser(
        email="admin.login@example.com",
        password_hash=hashed_pw,
        role=AdminRole.CEO
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)

    # 2. Action: Make login request
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin.login@example.com", "password": plain_password}
    )

    # 3. Assert: Correct response
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    # Cleanup
    await db_session.delete(admin)
    await db_session.commit()


@pytest.mark.asyncio
async def test_login_wrong_password_participant(client: httpx.AsyncClient, db_session: AsyncSession):
    # 1. Setup: Create a participant
    plain_password = "correct_password_p"
    hashed_pw = hash_password(plain_password)
    participant = User(
        full_name="Test Participant WrongPass",
        email="participant.wrongpass@example.com",
        password_hash=hashed_pw,
        phone_number="+254712345002",
        status=UserStatus.ACTIVE
    )
    db_session.add(participant)
    await db_session.commit()
    await db_session.refresh(participant)

    # 2. Action: Make login request with wrong password
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "participant.wrongpass@example.com", "password": "wrong_password_p"}
    )

    # 3. Assert: 401 Unauthorized
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid email or password"

    # Cleanup
    await db_session.delete(participant)
    await db_session.commit()


@pytest.mark.asyncio
async def test_login_wrong_password_admin(client: httpx.AsyncClient, db_session: AsyncSession):
    # 1. Setup: Create an admin
    plain_password = "correct_password_a"
    hashed_pw = hash_password(plain_password)
    admin = AdminUser(
        email="admin.wrongpass@example.com",
        password_hash=hashed_pw,
        role=AdminRole.FINANCE
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)

    # 2. Action: Make login request with wrong password
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin.wrongpass@example.com", "password": "wrong_password_a"}
    )

    # 3. Assert: 401 Unauthorized
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid email or password"

    # Cleanup
    await db_session.delete(admin)
    await db_session.commit()


@pytest.mark.asyncio
async def test_login_email_not_found(client: httpx.AsyncClient):
    # No setup needed as we are testing a non-existent email

    # 1. Action: Make login request with non-existent email
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent.user@example.com", "password": "anypassword"}
    )

    # 2. Assert: 401 Unauthorized
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid email or password"

# It's good practice to ensure unique emails/phone numbers if tests run in parallel
# or if the DB is not perfectly isolated per test.
# The current cleanup (delete) helps, but if a test fails before cleanup,
# subsequent runs might have issues with unique constraints.
# A robust test setup often involves transaction-based rollback or fresh DB per test.
# For now, manual cleanup is implemented.
# Also, these tests assume that the client fixture is correctly configured with base_url.
# And db_session provides a working asynchronous SQLAlchemy session.
# If these fixtures are not set up (e.g. in tests/conftest.py), these tests will fail.
# We also rely on `app.core.security.hash_password` being available and correct.
# The `bcrypt` package would be needed for `hash_password`.
# `passlib` is also used by the main code for verify_password.
# `sqlalchemy` for models.
# `fastapi` for the app itself.
# `httpx` for the client.
# `pytest` and `pytest-asyncio` for running.
