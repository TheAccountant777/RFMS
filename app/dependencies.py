from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session # Assuming database setup in app.core.database
from app.core.security import verify_token # Assuming JWT verification in app.core.security
from app.models.admin_user import AdminUser # Import AdminUser model
from app.models.user import User # Import User model (for checking if not admin)

# OAuth2PasswordBearer for token extraction from header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login") # Token endpoint will be implemented later

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides an async database session."""
    async with async_session() as session:
        yield session

async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """Dependency that gets the current authenticated user (admin or participant)."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_token(token) # Verify and decode the JWT token
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        # You might add token validity checks here (e.g., against a token blacklist)
    except Exception: # Catch potential errors during token verification
        raise credentials_exception

    # Try fetching from AdminUser first
    admin_user = await db.get(AdminUser, user_id)
    if admin_user:
        return admin_user

    # If not an admin, try fetching from User (participant)
    user = await db.get(User, user_id)
    if user:
        return user

    # If user_id from token doesn't match any user
    raise credentials_exception


async def get_current_admin_user(current_user: object = Depends(get_current_user)):
    """Dependency that gets the current authenticated user and checks if they are an admin."""
    # Assuming your User and AdminUser models have a way to identify their type or role
    # This check depends on how you differentiate admin and regular users in your models/logic.
    # For now, we'll assume get_current_user returns an AdminUser object if it's an admin.
    # You might need to adjust this based on your actual user model structure.
    from app.models.admin_user import AdminUser # Import here to avoid circular dependency if AdminUser imports dependencies

    if not isinstance(current_user, AdminUser):
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted for non-admin users",
        )
    return current_user