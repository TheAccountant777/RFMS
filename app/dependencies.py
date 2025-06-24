from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError

from app.core.database import get_db # Import get_db from database module
from app.core.security import verify_token # Assuming JWT verification in app.core.security
from app.models.admin_user import AdminUser # Import AdminUser model
from app.models.user import User # Import User model (for checking if not admin)

# OAuth2PasswordBearer for token extraction from header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login") # Token endpoint will be implemented later

async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """Dependency that gets the current authenticated user (admin or participant)."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_token(token) # Verify and decode the JWT token
        if payload is None: # Token is invalid (expired, malformed, bad signature)
            raise credentials_exception

        token_type = payload.get("type")
        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type, expected access token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id: str = payload.get("sub")
        if user_id is None:
            # This case should ideally be caught by verify_token if sub is mandatory
            # or further validation of payload structure.
            raise credentials_exception

        # You might add token validity checks here (e.g., against a token blacklist)
    except JWTError: # Specifically catch JWT errors from verify_token
        raise credentials_exception
    except Exception: # Catch other potential errors
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

async def get_current_active_participant(user_from_token: any = Depends(get_current_user)) -> User:
    """
    Dependency that gets the current authenticated user, ensures they are a
    participant (User model) and are active.
    Raises HTTPException 403 if user is not a participant.
    Raises HTTPException 401 if user is inactive or for other auth issues via get_current_user.
    """
    from app.models.user import User # Ensure User model is imported
    # Assuming User model has a 'status' attribute similar to 'user_status' ENUM from TDD
    # and an equivalent to UserStatus.ACTIVE. For now, we'll check its instance.
    # The actual status check (e.g. user_from_token.status == UserStatus.ACTIVE)
    # needs to be adapted if the User model has a specific active/inactive field.

    if not isinstance(user_from_token, User):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Participant role required",
        )

    # Check if the participant user is active.
    # This requires UserStatus enum to be defined in app.models.user
    from app.models.user import UserStatus # Assuming UserStatus is defined here
    if hasattr(user_from_token, 'status') and user_from_token.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not active",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Also, ensure the token used was an "access" token.
    # get_current_user internally calls verify_token(token) but doesn't check type.
    # We need to re-verify or ensure verify_token can pass back the payload for type checking.
    # For now, this check is missing here but should be in get_current_user or verify_token.
    # Plan step 5 mentioned checking type in the dependency: "Verify payload.get("type") == "access" "
    # This part of the logic will be revisited if tests fail due to type issues.

    return user_from_token