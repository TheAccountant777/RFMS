from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_participant, get_db
from app.models.user import User # Required for Depends type hint
from app.schemas.user import ParticipantProfileResponse

router = APIRouter(
    prefix="/participant", # Assuming a prefix for participant specific routes
    tags=["Participant"]
)

@router.get("/me", response_model=ParticipantProfileResponse)
async def read_participant_me(
    current_user: User = Depends(get_current_active_participant)
):
    """
    Get current logged-in participant's profile information.
    """
    # current_user is already validated by the dependency get_current_active_participant
    # Pydantic will automatically map the User ORM model to ParticipantProfileResponse
    return current_user
