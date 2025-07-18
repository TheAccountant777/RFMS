from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import ParticipantRegisterPayload, JWTTokens
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