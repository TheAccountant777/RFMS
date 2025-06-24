from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_admin_user # Assuming these dependencies exist
from app.services.auth_service import AuthService
from app.schemas.invitation import InvitationCreateResponse # Assuming this schema exists
from app.exceptions import ConflictError # Import the custom exception

router = APIRouter(prefix="/admin/invitations", tags=["Admin - Invitations"])

@router.post(
    "/",
    response_model=InvitationCreateResponse, # Define response model
    status_code=status.HTTP_201_CREATED,
    summary="Create and send a participant invitation",
    description="Creates a new invitation record and sends an email to the prospective participant. Requires Admin authentication."
)
async def create_invitation(
    email: str, # Input for the email address
    db: AsyncSession = Depends(get_db),
    current_admin_user: dict = Depends(get_current_admin_user) # Secure the endpoint for admins
):
    """
    Handles the creation and sending of a participant invitation.
    """
    auth_service = AuthService(db)
    try:
        invitation = await auth_service.create_invitation(email)
        return InvitationCreateResponse(
            id=invitation.id,
            email=invitation.email,
            token=invitation.token, # Include token in response for testing/debugging, remove in production if not needed
            expires_at=invitation.expires_at,
            status=invitation.status,
            created_at=invitation.created_at
        )
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        # Catch other potential errors during invitation creation or email sending
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create invitation: {e}"
        )