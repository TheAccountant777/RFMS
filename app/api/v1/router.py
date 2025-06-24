from fastapi import APIRouter

from .admin import invitations as admin_invitations_router # Import the admin invitations router
from .auth import router as auth_router # Import the auth router
from .participant import endpoints as participant_router # Import the participant router

api_router = APIRouter()

# Include the admin invitations router
api_router.include_router(admin_invitations_router.router)

# Include the auth router with prefix
api_router.include_router(auth_router, prefix="/auth")

# Include the participant router
# The prefix "/participant" is already defined in participant_router.router
api_router.include_router(participant_router.router)