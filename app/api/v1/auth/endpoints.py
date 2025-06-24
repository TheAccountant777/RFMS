from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm # Will not use this as per previous decision

from app.dependencies import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import ParticipantRegisterPayload, JWTTokens, LoginPayload # Added LoginPayload
from app.exceptions import NotFoundError, ConflictError, ValidationError

router = APIRouter(tags=["Authentication"])

@router.post(
    "/register",
    response_model=JWTTokens,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new participant",
    description="Registers a new participant using an invitation token. Returns JWT tokens for immediate login."
)
async def register_participant(
    user_data: ParticipantRegisterPayload,
    invitation_token: str = Query(..., description="The token from the invitation email"),
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new participant using an invitation token.
    
    - **invitation_token**: The token from the invitation email (query parameter)
    - **full_name**: The participant's full name
    - **password**: The participant's password (min 8 characters)
    - **phone_number**: The participant's phone number (must be a valid Kenyan mobile number)
    
    Returns JWT tokens for immediate login.
    """
    auth_service = AuthService(db)
    
    try:
        tokens = await auth_service.register_participant(invitation_token, user_data)
        return tokens
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        # Log the exception for debugging
        print(f"Error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration"
        )

@router.post(
    "/login",
    response_model=JWTTokens,
    status_code=status.HTTP_200_OK,
    summary="Login for participants and admins",
    description="Authenticates a user (participant or admin) and returns JWT tokens."
)
async def login(
    login_data: LoginPayload, # Using LoginPayload as per TDD and schema availability
    db: AsyncSession = Depends(get_db)
):
    """
    Login for existing users (participants or admins).

    - **email**: User's email
    - **password**: User's password

    Returns JWT access and refresh tokens.
    """
    auth_service = AuthService(db)
    # HTTPException from login_user will be automatically handled by FastAPI
    tokens = await auth_service.login_user(email=login_data.email, password=login_data.password)
    return tokens